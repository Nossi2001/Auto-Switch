# pages/router_configurator_page.py

import re
from collections import Counter
from PyQt6 import QtWidgets, QtCore
from tmp_router import tmp_router
from threads.interface_thread import InterfaceThread
from threads.configuration_thread import ConfigurationThread
from utils.ui_helpers import set_window_size_percentage
from config import description_color  # Importujemy słownik z config.py


class PortButton(QtWidgets.QPushButton):
    """
    Custom button representing a port with dynamic color palette.
    """

    def __init__(self, label='', parent=None, palette=None):
        super().__init__(label, parent)
        self.setCheckable(True)
        self.palette = palette or {
            'normal': '#5F5F5F',
            'hover': '#6F6F6F',
            'checked': '#505358'
        }  # Domyślna paleta
        self.setStyleSheet(self.get_style())
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

    def get_style(self):
        """
        Zwraca odpowiedni styl dla przycisku na podstawie palety kolorów.
        """
        return f"""
            QPushButton {{
                background-color: {self.palette['normal']};
                border: 3px solid #9E9E9E;
                border-radius: 5px;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-color: #4CAF50;
                background-color: {self.palette['hover']};
            }}
            QPushButton:checked {{
                background-color: {self.palette['checked']};
                border-color: #388E3C;
            }}
        """

    def update_style(self):
        """
        Aktualizuje styl przycisku. Należy wywołać, jeśli paleta się zmieni.
        """
        self.setStyleSheet(self.get_style())


class RouterConfiguratorPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.router = None
        self.init_ui()

    def initialize(self, router_ip, username, password):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.router = tmp_router(ip=self.router_ip, username=self.username, password=self.password)
        # Disable the interface until data is fetched
        self.setEnabled(False)
        # Start fetching interfaces in a separate thread
        self.interface_thread = InterfaceThread(self.router)
        self.interface_thread.interfaces_result.connect(self.on_interfaces_result)
        self.interface_thread.start()

    def init_ui(self):
        set_window_size_percentage(self)
        self.setWindowTitle("Router Configurator")
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #9E9E9E;
                margin-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #5F5F5F;
                border: 1px solid #9E9E9E;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
            QPushButton {
                background-color: #5F5F5F;
                border: 3px solid #9E9E9E;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                border-color: #4CAF50;
                background-color: #6F6F6F;
            }
            QPushButton:checked {
                background-color: #505358;
                border-color: #388E3C;
            }
        """)

        # Placeholder content until interfaces are fetched
        placeholder_label = QtWidgets.QLabel("Fetching interfaces...")
        placeholder_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(placeholder_label)

    def on_interfaces_result(self, success, interfaces, error_message):
        if success:
            # interfaces is now a dict: {interface_name: description}
            self.physical_interfaces = interfaces
            self.setup_ui_elements()
            self.setEnabled(True)
        else:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                f"Failed to fetch interfaces:\n{error_message}"
            )
            self.stacked_widget.setCurrentIndex(0)  # Return to StartPage
            self.router.disconnect()

    def setup_ui_elements(self):
        # Clear the main layout
        self.clear_layout(self.main_layout)

        # Sekcja Portów i Legenda
        self.setup_ports_section()

        # Sekcja Szablonów Konfiguracji
        self.setup_template_section()

        # Przycisk Zastosuj Konfigurację
        apply_button = QtWidgets.QPushButton("Apply Configuration")
        apply_button.clicked.connect(self.apply_configuration)
        self.main_layout.addWidget(apply_button)

    def clear_layout(self, layout):
        """
        Removes all widgets from a layout.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clear_layout(sub_layout)

    def setup_ports_section(self):
        """
        Sets up the ports section with a dynamic grid of port buttons and legend.
        """
        ports_group = QtWidgets.QGroupBox("Ports")
        ports_layout = QtWidgets.QVBoxLayout()
        ports_group.setLayout(ports_layout)

        # Ustawienie proporcji wysokości: 45% głównego okna
        ports_group.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        # Dodanie stretch factor do ports_layout
        # Główny layout będzie zarządzać proporcjami

        # Container z tłem i marginesami
        ports_container = QtWidgets.QWidget()
        ports_container.setStyleSheet("background-color: #3C3C3C;")  # Adjusted background color
        container_layout = QtWidgets.QVBoxLayout()
        container_layout.setContentsMargins(10, 10, 10, 10)  # Margin
        ports_container.setLayout(container_layout)

        # Grid layout dla portów
        grid_widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(10)  # Set spacing between ports to 10px
        grid_widget.setLayout(grid_layout)

        # Definicja liczby portów
        self.port_count = 5
        self.port_buttons = {}
        columns = 5  # 5 columns
        rows = 1  # 1 row

        # Konwersja słownika interfejsów na listę krotek
        interfaces_list = list(self.physical_interfaces.items())

        for index in range(self.port_count):
            row_idx = index // columns
            col_idx = index % columns

            port_number = index + 1
            port_label = str(port_number)

            # Pobranie odpowiedniego interfejsu i opisu, jeśli istnieje
            if index < len(interfaces_list):
                interface_name, description = interfaces_list[index]
            else:
                interface_name = f"Port {port_number}"
                description = "No description available."

            # Pobranie palety kolorów z config.py na podstawie opisu
            palette = description_color.get(description, {
                'normal': '#5F5F5F',
                'hover': '#6F6F6F',
                'checked': '#505358'
            })  # Domyślna paleta jeśli opis nie jest w słowniku

            port_button = PortButton(port_label, palette=palette)
            port_button.setToolTip(description)  # Set description as the tooltip
            port_button.setText(port_label)
            port_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

            # Przechowywanie nazwy interfejsu w właściwości przycisku
            port_button.setProperty("interface_name", interface_name)

            self.port_buttons[port_label] = port_button
            grid_layout.addWidget(port_button, row_idx, col_idx)

        # Ustawienie stretch factors, aby osiągnąć proporcje (2:1 width:height)
        for i in range(columns):
            grid_layout.setColumnStretch(i, 2)  # Width proportion
        for i in range(rows):
            grid_layout.setRowStretch(i, 1)  # Height proportion

        container_layout.addWidget(grid_widget)

        # Dodanie sekcji Legenda bez tytułu
        self.setup_legend_section(container_layout)

        ports_layout.addWidget(ports_container)
        self.main_layout.addWidget(ports_group, stretch=9)  # 45% zakładając 20 jako całkowity stretch

    def setup_legend_section(self, parent_layout):
        """
        Sets up the legend section explaining the color codes without a title, embedded in Ports Section.
        """
        # Tworzymy widget na legendę
        legend_widget = QtWidgets.QWidget()
        legend_layout = QtWidgets.QHBoxLayout()
        legend_layout.setSpacing(20)  # Odstęp między wpisami w legendzie
        legend_widget.setLayout(legend_layout)

        # Iterujemy przez opis i kolory w config.py
        for description, colors in description_color.items():
            # Tworzymy poziomy layout dla każdego wpisu w legendzie
            legend_entry = QtWidgets.QHBoxLayout()

            # Tworzymy kolorowy prostokąt
            color_box = QtWidgets.QLabel()
            color_box.setFixedSize(20, 20)
            color_box.setStyleSheet(f"background-color: {colors['normal']}; border: 1px solid #000000;")
            legend_entry.addWidget(color_box)

            # Dodajemy opis
            description_label = QtWidgets.QLabel(description)
            description_label.setStyleSheet("color: #FFFFFF;")
            legend_entry.addWidget(description_label)

            # Dodajemy wpis do layoutu legendy
            legend_layout.addLayout(legend_entry)

        # Dodajemy legendę do parent_layout (Ports Container Layout)
        parent_layout.addWidget(legend_widget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    def setup_template_section(self):
        """
        Sets up the template selection section.
        """
        templates_group = QtWidgets.QGroupBox("Configuration Templates")
        templates_layout = QtWidgets.QVBoxLayout()
        templates_group.setLayout(templates_layout)

        # Ustawienie stylu dla QGroupBox (szablonów)
        templates_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #9E9E9E;
                margin-top: 20px;
                background-color: #3C3C3C;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)

        # Lista dostępnych szablonów
        self.templates = [
            "dhcp_server: Configure the router as a DHCP server.",
            "lan_dhcp: Configure LAN DHCP settings.",
            "data_configuration_without_bridge: Apply data configurations without bridging."
        ]

        # ComboBox do wyboru szablonu
        self.template_combo = QtWidgets.QComboBox()
        # Dodajemy tylko nazwę szablonu do ComboBox
        template_names = [template.split(":")[0] for template in self.templates]
        self.template_combo.addItems(template_names)
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)

        # Stylowanie ComboBox
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: #5F5F5F;
                border: 1px solid #9E9E9E;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox:focus {
                border: 1px solid #4CAF50;
            }
        """)

        templates_layout.addWidget(self.template_combo, stretch=1)

        # Etykieta wyświetlająca opis szablonu bezpośrednio pod dropdownem
        self.template_description = QtWidgets.QLabel()
        self.template_description.setWordWrap(True)
        self.template_description.setStyleSheet("color: #FFFFFF;")  # Ustawienie koloru dla etykiety opisu
        templates_layout.addWidget(self.template_description, stretch=1)

        # Dynamiczne pola wejściowe na podstawie wybranego szablonu
        self.dynamic_input_group = QtWidgets.QGroupBox("Configuration Parameters")
        self.dynamic_input_layout = QtWidgets.QFormLayout()
        self.dynamic_input_group.setLayout(self.dynamic_input_layout)

        # Stylowanie dla dynamicznych inputów
        self.dynamic_input_group.setStyleSheet("""
            QGroupBox {
                background-color: #3C3C3C;
                border: 1px solid #9E9E9E;
                border-radius: 5px;
                color: #FFFFFF;
            }
        """)

        templates_layout.addWidget(self.dynamic_input_group, stretch=8)

        self.main_layout.addWidget(templates_group, stretch=11)  # Pozostałe 55% zakładając total stretch=20

        # Inicjalizacja inputów dla pierwszego szablonu
        self.on_template_changed(0)

    def on_template_changed(self, index):
        """
        Updates the template description and dynamic inputs based on the selected template.
        """
        # Aktualizacja opisu szablonu
        description = self.templates[index].split(": ", 1)[1]
        self.template_description.setText(description)

        # Czyszczenie istniejących inputów
        self.clear_layout(self.dynamic_input_layout)

        # Tworzenie inputów na podstawie wybranego szablonu
        selected_template = self.templates[index].split(":")[0]

        if selected_template == "dhcp_server":
            self.name_server_input = QtWidgets.QLineEdit()
            self.name_server_input.setPlaceholderText("Name Server (e.g., 8.8.8.8)")
            self.dynamic_input_layout.addRow("Name Server:", self.name_server_input)

            self.gateway_input = QtWidgets.QLineEdit()
            self.gateway_input.setPlaceholderText("Gateway (e.g., 192.168.1.1)")
            self.dynamic_input_layout.addRow("Gateway:", self.gateway_input)

            self.netmask_input = QtWidgets.QLineEdit()
            self.netmask_input.setPlaceholderText("Netmask (e.g., 255.255.255.0)")
            self.dynamic_input_layout.addRow("Netmask:", self.netmask_input)

            self.dhcp_range_input = QtWidgets.QLineEdit()
            self.dhcp_range_input.setPlaceholderText("DHCP Range (e.g., 192.168.1.100 192.168.1.200)")
            self.dynamic_input_layout.addRow("DHCP Range Start and Stop:", self.dhcp_range_input)

        elif selected_template == "lan_dhcp":
            # Informacyjna etykieta
            info_label = QtWidgets.QLabel("LAN DHCP configuration will be applied to the selected ports.")
            info_label.setWordWrap(True)
            self.dynamic_input_layout.addRow(info_label)

        elif selected_template == "data_configuration_without_bridge":
            # Informacyjna etykieta
            info_label = QtWidgets.QLabel("Data configuration without bridge will be applied to the selected ports.")
            info_label.setWordWrap(True)
            self.dynamic_input_layout.addRow(info_label)

    def apply_configuration(self):
        selected_template_index = self.template_combo.currentIndex()
        selected_template = self.templates[selected_template_index].split(":")[0]

        # Lista wybranych portów do konfiguracji (używając nazw interfejsów przechowywanych w właściwościach)
        selected_ports = [
            btn.property("interface_name") for btn in self.port_buttons.values() if btn.isChecked()
        ]

        # Walidacja wyboru szablonu
        if not selected_template:
            QtWidgets.QMessageBox.warning(self, "Error", "No configuration template selected.")
            return

        # Walidacja wyboru portów
        if not selected_ports:
            QtWidgets.QMessageBox.warning(self, "No Ports Selected", "No ports selected for configuration.")
            return

        # Pobranie dynamicznych inputów na podstawie wybranego szablonu
        config_params = {}
        if selected_template == "dhcp_server":
            name_server = self.name_server_input.text()
            gateway = self.gateway_input.text()
            netmask = self.netmask_input.text()
            dhcp_range = self.dhcp_range_input.text()

            if not name_server or not gateway or not netmask or not dhcp_range:
                QtWidgets.QMessageBox.warning(self, "Error", "All fields are required for DHCP Server configuration.")
                return

            # Rozdzielenie zakresu DHCP na start i stop
            try:
                dhcp_range_start, dhcp_range_stop = dhcp_range.split()
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "Error",
                                              "DHCP Range must contain two addresses separated by a space.")
                return

            config_params = {
                "name_server": name_server,
                "gateway": gateway,
                "netmask": netmask,
                "dhcp_range_start": dhcp_range_start,
                "dhcp_range_stop": dhcp_range_stop
            }

        elif selected_template == "lan_dhcp":
            # Nie wymagane dodatkowe parametry
            config_params = {
                "ports": selected_ports
            }

        elif selected_template == "data_configuration_without_bridge":
            # Nie wymagane dodatkowe parametry
            config_params = {
                "ports": selected_ports
            }

        # Wyłączenie interfejsu
        self.setEnabled(False)

        # Uruchomienie konfiguracji w oddzielnym wątku
        self.configuration_thread = ConfigurationThread(
            self.router,
            selected_template,
            selected_ports,
            config_params  # Przekazanie dodatkowych parametrów
        )
        self.configuration_thread.configuration_result.connect(self.on_configuration_result)
        self.configuration_thread.start()

    def on_configuration_result(self, success, message):
        # Ponowne włączenie interfejsu
        self.setEnabled(True)

        if success:
            QtWidgets.QMessageBox.information(self, "Configuration", message)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        """
        Disconnects from the router when the window is closed.
        """
        if self.router:
            self.router.disconnect()
        event.accept()
