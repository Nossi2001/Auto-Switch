# pages/config_page.py

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QClipboard

from config import Cisco_Router, Cisco_Switch, description_color
from methods_data import methods_inputs, optional_params
from template_logic import TEMPLATE_FUNCTIONS, TemplateError, assign_interface_labels
from widgets.custom_widgets import PortButton, VLANLegend
from styles import BASE_STYLE, GROUPBOX_STYLE, LABEL_STYLE

class ConfigPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setContentsMargins(20, 20, 20, 20)  # Add margins
        self.device_type = None
        self.device_name = None
        self.methods = []
        self.physical_interfaces = []
        self.port_buttons = {}
        self.used_vlans = {}
        self.labeled_interfaces = []
        self.full_config = ""

        self.setStyleSheet(BASE_STYLE + GROUPBOX_STYLE + LABEL_STYLE)

        self.main_layout = QtWidgets.QVBoxLayout()
        placeholder_label = QtWidgets.QLabel("Proszę wybrać urządzenie na poprzedniej stronie...")
        placeholder_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(placeholder_label)
        self.setLayout(self.main_layout)

        self.params_group = None
        self.params_layout = None
        self.param_widgets = {}
        self.vlan_legend = None

    def initialize(self, device_type, device_name):
        self.device_type = device_type
        self.device_name = device_name
        self.used_vlans = {}
        self.full_config = ""

        if self.device_type == 'router':
            if device_name not in Cisco_Router:
                QtWidgets.QMessageBox.critical(self, "Error", f"Router '{device_name}' nie znaleziony.")
                return
            device_data = Cisco_Router[device_name]
            device_label = "Router"
        else:
            if device_name not in Cisco_Switch:
                QtWidgets.QMessageBox.critical(self, "Error", f"Switch '{device_name}' nie znaleziony.")
                return
            device_data = Cisco_Switch[device_name]
            device_label = "Switch"

        self.methods = device_data.get('method_list', [])
        self.physical_interfaces = device_data.get('interfaces', [])
        self.labeled_interfaces = assign_interface_labels(self.physical_interfaces)

        self.setup_ui_elements(device_label)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def setup_ui_elements(self, device_label):
        self.clear_layout(self.main_layout)
        header_label = QtWidgets.QLabel(f"Urządzenie: {self.device_name} ({device_label})")
        header_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header_label.setProperty("heading", True)
        header_label.setStyleSheet(BASE_STYLE)
        self.main_layout.addWidget(header_label)

        device_description = Cisco_Router[self.device_name]['description'] if self.device_type == 'router' else Cisco_Switch[self.device_name]['description']
        colors = description_color.get(device_description, {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'})

        # Sekcja portów
        ports_group = QtWidgets.QGroupBox("Porty (zaznacz interfejsy dla wybranej metody)")
        ports_layout = QtWidgets.QVBoxLayout()
        ports_group.setLayout(ports_layout)
        ports_container = QtWidgets.QWidget()

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(5)
        columns = 14
        row = 0
        col = 0

        self.port_buttons = {}
        for iface in self.labeled_interfaces:
            port_label = iface['label']
            btn = PortButton(port_label)
            btn.setProperty("interface_name", iface['name'])
            btn.set_color(colors['normal'])
            self.port_buttons[port_label] = btn

            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        ports_container.setLayout(grid_layout)
        ports_layout.addWidget(ports_container)
        self.main_layout.addWidget(ports_group)

        # Sekcja metod
        methods_group = QtWidgets.QGroupBox("Metody")
        methods_layout = QtWidgets.QVBoxLayout()
        methods_group.setLayout(methods_layout)

        self.method_combo = QtWidgets.QComboBox()
        self.method_combo.addItems(self.methods)
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        methods_layout.addWidget(self.method_combo)
        methods_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.params_group = QtWidgets.QGroupBox("Parametry Metody")
        self.params_layout = QtWidgets.QFormLayout()
        self.params_group.setLayout(self.params_layout)
        methods_layout.addWidget(self.params_group)
        self.main_layout.addWidget(methods_group)

        # Przycisk Zastosuj Konfigurację
        apply_button = QtWidgets.QPushButton("Zastosuj Konfigurację")
        apply_button.clicked.connect(self.apply_configuration)
        self.main_layout.addWidget(apply_button)

        # Dolne przyciski
        bottom_layout = QtWidgets.QHBoxLayout()

        back_button = QtWidgets.QPushButton("Wróć")
        back_button.clicked.connect(self.go_back)
        bottom_layout.addWidget(back_button)

        copy_button = QtWidgets.QPushButton("Skopiuj całą konfigurację")
        copy_button.clicked.connect(self.copy_entire_config)
        bottom_layout.addWidget(copy_button)

        save_button = QtWidgets.QPushButton("Prześlij do pliku")
        save_button.clicked.connect(self.save_entire_config)
        bottom_layout.addWidget(save_button)

        self.main_layout.addLayout(bottom_layout)

        # Legenda VLAN
        self.vlan_legend = VLANLegend()
        self.main_layout.addWidget(self.vlan_legend)

        self.on_method_changed(self.method_combo.currentIndex())

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)

    def copy_entire_config(self):
        cb = QtWidgets.QApplication.clipboard()
        cb.setText(self.full_config, mode=QClipboard.Mode.Clipboard)
        QtWidgets.QMessageBox.information(self, "Skopiowano", "Cała konfiguracja została skopiowana do schowka.")

    def save_entire_config(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz konfigurację", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(self.full_config)
                QtWidgets.QMessageBox.information(self, "Zapisano", "Konfiguracja zapisana do pliku.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać pliku: {e}")

    def on_method_changed(self, index):
        self.clear_layout(self.params_layout)
        self.param_widgets = {}
        method_name = self.method_combo.currentText()
        input_params = methods_inputs.get(method_name, [])
        opt = optional_params.get(method_name, [])

        for p in input_params:
            label_text = p
            if p in opt:
                label_text += " (opcjonalne)"
            widget = self.create_input_widget(p, method_name)
            self.params_layout.addRow(label_text + ":", widget)
            self.param_widgets[p] = widget

        self.update_dynamic_fields()

    def create_input_widget(self, param_name, method_name):
        lower = param_name.lower()

        # Walidatory
        ip_regex = QRegularExpression("^(25[0-5]|2[0-4]\\d|[01]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[01]?\\d?\\d)){3}$")
        ip_validator = QRegularExpressionValidator(ip_regex)

        # Dla protokołów routingu
        if "routing protocol" in lower:
            combo = QtWidgets.QComboBox()
            combo.addItems(["OSPF", "EIGRP"])
            return combo

        # Dla booleanów
        if "dhcp server" in lower or "vlan routing" in lower:
            chk = QtWidgets.QCheckBox()
            return chk

        if param_name == "Interface Role":
            combo = QtWidgets.QComboBox()
            combo.addItems(["Inside", "Outside"])  # Dodajemy dostępne opcje
            return combo

        # Dla VLAN Mode
        if param_name == "VLAN Mode":
            mode_group = QtWidgets.QGroupBox()
            mode_layout = QtWidgets.QHBoxLayout()
            static_rb = QtWidgets.QRadioButton("Static")
            dynamic_rb = QtWidgets.QRadioButton("Dynamic")
            static_rb.setChecked(True)
            mode_layout.addWidget(static_rb)
            mode_layout.addWidget(dynamic_rb)
            mode_group.setLayout(mode_layout)
            mode_group.setProperty("static_rb", static_rb)
            mode_group.setProperty("dynamic_rb", dynamic_rb)
            return mode_group

        # Dla ID i liczb
        if ("vlan id" in lower or "process id" in lower or "area id" in lower or
            "voice vlan id" in lower or "native vlan id" in lower or "lease time" in lower):
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, 65535)
            return spin

        # Dla maski podsieci
        if "subnet mask" in lower or "netmask" in lower:
            mask_line = QtWidgets.QLineEdit()
            mask_line.setValidator(ip_validator)
            mask_line.setPlaceholderText("np. 255.255.255.0")
            return mask_line

        # Dla sieci (w dynamicznym routingu)
        if param_name == "Networks":
            txt = QtWidgets.QPlainTextEdit()
            txt.setPlaceholderText("Wpisz sieci oddzielone średnikiem (np. 192.168.1.0/24;10.0.0.0/8).")
            txt.setFixedHeight(60)
            return txt

        # Dla IP (Default Router, Pool Start/End IP, DNS Server)
        if ("ip" in lower or "router" in lower or "dns" in lower or "network" in lower):
            ip_line = QtWidgets.QLineEdit()
            ip_line.setValidator(ip_validator)
            ip_line.setPlaceholderText("np. 192.168.1.1")
            return ip_line

        # Dla nazw (Pool Name, Profile Name, Domain Name)
        if "name" in lower:
            line = QtWidgets.QLineEdit()
            line.setPlaceholderText("Wprowadź nazwę")
            return line

        # Dla opisów
        if "description" in lower:
            line = QtWidgets.QLineEdit()
            line.setPlaceholderText("Opis (opcjonalnie)")
            return line

        # Dla koloru
        if "color" in lower:
            btn = QtWidgets.QPushButton("Wybierz Kolor")
            btn.clicked.connect(lambda _, b=btn: self.select_color(b))
            return btn

        # Dla Allowed VLANs lub Access List
        if "allowed vlans" in lower or "access list" in lower:
            line = QtWidgets.QLineEdit()
            if "allowed vlans" in lower:
                line.setPlaceholderText("np. 10,20,30")
            else:
                line.setPlaceholderText("Wpisz ACL (np. 100)")
            return line

        # Domyślnie QLineEdit
        line = QtWidgets.QLineEdit()
        line.setPlaceholderText("Wprowadź wartość")
        return line

    def select_color(self, button):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            button.setStyleSheet(f"background-color: {hex_color};")
            button.setProperty("selected_color", hex_color)

    def update_dynamic_fields(self):
        method_name = self.method_combo.currentText()

        # Reset all port buttons to default state
        for btn in self.port_buttons.values():
            btn.setEnabled(True)
            btn.setChecked(False)

        # Method-specific behaviors
        if method_name == 'set_access_vlan':
            # Enable VLAN-related fields
            for param_name, widget in self.param_widgets.items():
                if 'vlan' in param_name.lower():
                    widget.setEnabled(True)
                    if isinstance(widget, QtWidgets.QLineEdit):
                        widget.setPlaceholderText("Enter VLAN ID (1-4094)")

        elif method_name == 'apply_nat':
            # For NAT, we need at least one inside and one outside interface
            if 'Interface Role' in self.param_widgets:
                self.param_widgets['Interface Role'].currentTextChanged.connect(
                    lambda: self.update_nat_interface_requirements()
                )

        elif method_name == 'apply_dhcp_server':
            # Show DNS and lease time fields only when DHCP is enabled
            if 'DNS Server' in self.param_widgets:
                self.param_widgets['DNS Server'].setVisible(True)
            if 'Lease Time' in self.param_widgets:
                self.param_widgets['Lease Time'].setVisible(True)

        elif method_name == 'restart_device':
            # Disable all port selection for device restart
            for btn in self.port_buttons.values():
                btn.setEnabled(False)
                btn.setChecked(False)

        self.update_method_description(method_name)

    def update_method_description(self, method_name):
        """Updates the description label for the selected method."""
        descriptions = {
            'apply_dynamic_routing': "Routing dynamiczny dla wybranego intrefejsu",
            'set_access_vlan': "Konfiguracja portów w trybie dostępowym VLAN",
            'apply_nat': "Konfiguracja NAT z interfejsami wewnętrznymi/zewnętrznymi",
            'apply_dhcp_server': "Konfiguracja serwera DHCP na wybranych interfejsach",
            'restart_device': "Przywracanie urządzenia do ustawień fabrycznych",
            'default_interface': "Resetowanie wybranych interfejsów do konfiguracji domyślnej"
        }

        if hasattr(self, 'method_description_label'):
            self.method_description_label.deleteLater()

        description = descriptions.get(method_name, "Konfiguracja wybranych interfejsów")
        self.method_description_label = QtWidgets.QLabel(description)
        self.method_description_label.setProperty("heading", "true")
        self.method_description_label.setStyleSheet(BASE_STYLE)
        self.params_layout.insertRow(0, self.method_description_label)

    def update_nat_interface_requirements(self):
        """Updates interface requirements for NAT configuration."""
        current_role = self.param_widgets['Interface Role'].currentText()
        for btn in self.port_buttons.values():
            btn.setEnabled(True)

    def apply_configuration(self):
        selected_method = self.method_combo.currentText()
        selected_ports = [btn.property("interface_name") for btn in self.port_buttons.values() if btn.isChecked()]

        try:
            params_values = self.collect_param_values(selected_method)

            func = TEMPLATE_FUNCTIONS.get(selected_method, None)
            if not func:
                QtWidgets.QMessageBox.warning(self, "Błąd", f"Brak logiki dla metody: {selected_method}")
                return
            if selected_method == "default_interface":
                # Resetowanie kolorów w GUI
                for port in selected_ports:
                    for btn in self.port_buttons.values():
                        if btn.property("interface_name") == port:
                            btn.set_color('#5F5F5F')  # Resetuj kolor
            if selected_method == "restart_device":
                for btn in self.port_buttons.values():
                    btn.set_color('#5F5F5F')
                self.vlan_legend.clear_legends()

            if selected_method in ["apply_data_template", "set_access_vlan", "set_trunk_vlan", "set_native_vlan"]:
                config_text = func(params_values, selected_ports, self.used_vlans)
            else:
                config_text = func(params_values, selected_ports)

            if config_text.strip():
                if self.full_config.strip():
                    self.full_config += "\n! --- Kolejna konfiguracja ---\n"
                self.full_config += config_text + "\n"

            QtWidgets.QMessageBox.information(self, "Wygenerowana Konfiguracja", config_text)

            # Aktualizacja kolorów portów i legendy VLAN
            self.update_vlan_visuals(selected_method)  # Wywołanie aktualizacji wizualnej

        except TemplateError as e:
            QtWidgets.QMessageBox.warning(self, "Błąd Walidacji", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Błąd", f"Nieoczekiwany błąd: {e}")

    def collect_param_values(self, selected_method):
        input_params = methods_inputs.get(selected_method, [])
        opt = optional_params.get(selected_method, [])
        params_values = {}
        for label, widget in self.param_widgets.items():
            if label == "VLAN Mode":
                static_rb = widget.property("static_rb")
                dynamic_rb = widget.property("dynamic_rb")
                params_values[label] = "Static" if static_rb.isChecked() else "Dynamic"
            elif isinstance(widget, QtWidgets.QSpinBox):
                params_values[label] = widget.value()
            elif isinstance(widget, QtWidgets.QCheckBox):
                params_values[label] = widget.isChecked()
            elif isinstance(widget, QtWidgets.QComboBox):
                params_values[label] = widget.currentText()
            elif isinstance(widget, QtWidgets.QPushButton) and "color" in label.lower():
                params_values[label] = widget.property("selected_color") or ""
            elif isinstance(widget, QtWidgets.QPlainTextEdit):
                params_values[label] = widget.toPlainText().strip()
            elif isinstance(widget, QtWidgets.QLineEdit):
                params_values[label] = widget.text().strip()
            else:
                params_values[label] = ""
        return params_values

    def update_vlan_visuals(self, selected_method):
        """Aktualizuje kolory przycisków portów oraz legendę VLAN."""
        if selected_method in ["set_access_vlan", "apply_data_template", "set_trunk_vlan", "set_native_vlan"]:
            # Store current button states and colors
            button_states = {btn.property("interface_name"): (btn.isChecked(), btn.vlan_color)
                           for btn in self.port_buttons.values()}

            for vlan_id, vlan_info in self.used_vlans.items():
                # Dodaj VLAN do legendy
                self.vlan_legend.add_vlan(vlan_id, vlan_info['name'], vlan_info['color'])
                # Aktualizuj kolor przypisanych portów
                for port_name, btn in self.port_buttons.items():
                    interface_name = btn.property("interface_name")
                    if btn.isChecked() and interface_name in button_states:
                        btn.set_color(vlan_info['color'])
                    elif not btn.isChecked() and interface_name in button_states:
                        # Restore previous color if unchecked
                        prev_checked, prev_color = button_states[interface_name]
                        if prev_color:
                            btn.set_color(prev_color)
