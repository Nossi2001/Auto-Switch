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

        device_data = None
        device_label = None
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
        if layout:
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
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.main_layout.addWidget(header_label)

        device_description = ""
        if self.device_type == 'router':
            device_description = Cisco_Router[self.device_name]['description']
        else:
            device_description = Cisco_Switch[self.device_name]['description']
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

    def create_input_widget(self, param_name, method_name):
        lower = param_name.lower()

        # Walidator IP
        ip_regex = QRegularExpression("^(25[0-5]|2[0-4]\\d|[01]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[01]?\\d?\\d)){3}$")
        ip_validator = QRegularExpressionValidator(ip_regex)

        # Dla Interface Role (radio button)
        if param_name == "Interface Role":
            # Tworzymy dwa radio buttony: Inside i Outside
            role_group = QtWidgets.QGroupBox()
            role_layout = QtWidgets.QHBoxLayout()
            inside_rb = QtWidgets.QRadioButton("Inside")
            outside_rb = QtWidgets.QRadioButton("Outside")
            inside_rb.setChecked(True)  # domyślnie Inside
            role_layout.addWidget(inside_rb)
            role_layout.addWidget(outside_rb)
            role_group.setLayout(role_layout)
            # Zapamiętujemy referencje do radio buttonów
            role_group.setProperty("inside_rb", inside_rb)
            role_group.setProperty("outside_rb", outside_rb)
            return role_group

        if "ip" in lower or "router" in lower or "dns" in lower or "network" in lower:
            ip_line = QtWidgets.QLineEdit()
            ip_line.setValidator(ip_validator)
            ip_line.setPlaceholderText("np. 192.168.1.1")
            return ip_line

        if "pool name" in lower:
            line = QtWidgets.QLineEdit()
            line.setPlaceholderText("Nazwa puli NAT")
            return line

        if "pool start ip" in lower:
            ip_line = QtWidgets.QLineEdit()
            ip_line.setValidator(ip_validator)
            ip_line.setPlaceholderText("np. 203.0.113.10")
            return ip_line

        if "pool end ip" in lower:
            ip_line = QtWidgets.QLineEdit()
            ip_line.setValidator(ip_validator)
            ip_line.setPlaceholderText("np. 203.0.113.20")
            return ip_line

        if "access list" in lower:
            line = QtWidgets.QLineEdit()
            line.setPlaceholderText("np. 1 lub 100")
            return line

        if "netmask" in lower:
            mask_line = QtWidgets.QLineEdit()
            mask_line.setValidator(ip_validator)
            mask_line.setPlaceholderText("np. 255.255.255.0")
            return mask_line

        # Domyślny widget:
        line = QtWidgets.QLineEdit()
        return line

    def apply_configuration(self):
        selected_method = self.method_combo.currentText()
        selected_ports = [btn.property("interface_name") for btn in self.port_buttons.values() if btn.isChecked()]

        try:
            params_values = self.collect_param_values(selected_method)
            func = TEMPLATE_FUNCTIONS.get(selected_method, None)

            if not func:
                QtWidgets.QMessageBox.warning(self, "Błąd", f"Brak logiki dla metody: {selected_method}")
                return

            config_text = func(params_values, selected_ports)
            if config_text.strip():
                if self.full_config.strip():
                    self.full_config += "\n! --- Kolejna konfiguracja ---\n"
                self.full_config += config_text + "\n"

            QtWidgets.QMessageBox.information(self, "Wygenerowana Konfiguracja", config_text)

        except TemplateError as e:
            QtWidgets.QMessageBox.warning(self, "Błąd Walidacji", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Błąd", f"Nieoczekiwany błąd: {e}")

    def collect_param_values(self, selected_method):
        input_params = methods_inputs.get(selected_method, [])
        params_values = {}
        for label, widget in self.param_widgets.items():
            if label == "VLAN Mode":
                static_rb = widget.property("static_rb")
                dynamic_rb = widget.property("dynamic_rb")
                params_values[label] = "Static" if static_rb.isChecked() else "Dynamic"
            elif label == "Interface Role":
                # Pobierz wartość z radio buttonów:
                inside_rb = widget.property("inside_rb")
                outside_rb = widget.property("outside_rb")
                if inside_rb.isChecked():
                    params_values[label] = "Inside"
                elif outside_rb.isChecked():
                    params_values[label] = "Outside"
            elif isinstance(widget, QtWidgets.QSpinBox):
                params_values[label] = widget.value()
            elif isinstance(widget, QtWidgets.QCheckBox):
                params_values[label] = widget.isChecked()
            elif isinstance(widget, QtWidgets.QComboBox):
                params_values[label] = widget.currentText()
            elif isinstance(widget, QtWidgets.QLineEdit):
                params_values[label] = widget.text().strip()
            elif isinstance(widget, QtWidgets.QPlainTextEdit):
                params_values[label] = widget.toPlainText().strip()
            else:
                params_values[label] = ""
        return params_values
