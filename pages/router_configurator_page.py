import re
from collections import Counter
from PyQt6 import QtWidgets, QtCore
from tmp_router import tmp_router
from threads.interface_thread import InterfaceThread
from threads.configuration_thread import ConfigurationThread
from utils.ui_helpers import set_window_size_percentage


class PortButton(QtWidgets.QPushButton):
    """
    Custom button representing a port with hover effect.
    """
    def __init__(self, label='', parent=None):
        super().__init__(label, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)


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
            # List of physical interfaces
            self.physical_interfaces = interfaces  # List of interface names
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

        # Section 1: Ports
        self.setup_ports_section()

        # Section 2: Template Selection
        self.setup_template_section()

        # Section 3: Apply Button
        apply_button = QtWidgets.QPushButton("Apply Configuration")
        apply_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px; font-size: 18px; border-radius: 5px; margin-top: 20px;")
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
        Sets up the ports section with a dynamic grid of port buttons.
        """
        ports_group = QtWidgets.QGroupBox("Ports")
        ports_layout = QtWidgets.QVBoxLayout()
        ports_group.setLayout(ports_layout)

        # Container with background color and margins
        ports_container = QtWidgets.QWidget()
        ports_container.setStyleSheet("background-color: #3C3C3C;")  # Adjusted background color
        container_layout = QtWidgets.QVBoxLayout()
        container_layout.setContentsMargins(10, 10, 10, 10)  # Margin
        ports_container.setLayout(container_layout)

        # Grid layout for ports
        grid_widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(10)  # Set spacing between ports to 10px
        grid_widget.setLayout(grid_layout)

        # Define number of ports
        self.port_count = 5
        self.port_buttons = {}
        columns = 5  # 12 columns
        rows = 1      # 2 rows

        for index in range(self.port_count):
            row = index // columns
            col = index % columns

            port_number = index + 1
            port_label = str(port_number)

            # Get corresponding physical interface, if exists
            if index < len(self.physical_interfaces):
                interface_name = self.physical_interfaces[index]
            else:
                interface_name = f"Port {port_number}"

            port_button = PortButton(port_label)
            port_button.setToolTip(interface_name)  # Set description as the tooltip
            port_button.setText(port_label)
            port_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

            self.port_buttons[port_label] = port_button
            grid_layout.addWidget(port_button, row, col)

        # Set stretch factors to achieve proportions (2:1 width:height)
        for i in range(columns):
            grid_layout.setColumnStretch(i, 2)  # Width proportion
        for i in range(rows):
            grid_layout.setRowStretch(i, 1)     # Height proportion

        container_layout.addWidget(grid_widget)
        ports_layout.addWidget(ports_container)
        self.main_layout.addWidget(ports_group)

    def setup_template_section(self):
        """
        Sets up the template selection section.
        """
        templates_group = QtWidgets.QGroupBox("Configuration Templates")
        templates_layout = QtWidgets.QVBoxLayout()
        templates_group.setLayout(templates_layout)

        # List of available templates
        self.templates = [
            "dhcp_server: Configure the router as a DHCP server.",
            "lan_dhcp: Configure LAN DHCP settings.",
            "data_configuration_without_bridge: Apply data configurations without bridging."
        ]

        # ComboBox for template selection
        self.template_combo = QtWidgets.QComboBox()
        # Add only the template name to the ComboBox
        template_names = [template.split(":")[0] for template in self.templates]
        self.template_combo.addItems(template_names)
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        templates_layout.addWidget(self.template_combo)

        # Label for displaying the template description directly under the dropdown
        self.template_description = QtWidgets.QLabel()
        self.template_description.setWordWrap(True)
        templates_layout.addWidget(self.template_description)

        # Dynamic input fields based on the selected template
        self.dynamic_input_group = QtWidgets.QGroupBox("Configuration Parameters")
        self.dynamic_input_layout = QtWidgets.QFormLayout()
        self.dynamic_input_group.setLayout(self.dynamic_input_layout)
        templates_layout.addWidget(self.dynamic_input_group)

        self.main_layout.addWidget(templates_group)

        # Initialize inputs for the first template
        self.on_template_changed(0)

    def on_template_changed(self, index):
        """
        Updates the template description and dynamic inputs based on the selected template.
        """
        # Update the template description
        description = self.templates[index].split(": ", 1)[1]
        self.template_description.setText(description)

        # Clear existing inputs
        for i in reversed(range(self.dynamic_input_layout.count())):
            widget = self.dynamic_input_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add relevant input fields based on the selected template
        if index == 0:  # dhcp_server
            self.add_input_field("IP Address", "192.168.1.1")
            self.add_input_field("Subnet Mask", "255.255.255.0")
        elif index == 1:  # lan_dhcp
            self.add_input_field("DHCP Range Start", "192.168.1.100")
            self.add_input_field("DHCP Range End", "192.168.1.200")
        elif index == 2:  # data_configuration_without_bridge
            self.add_input_field("Data IP Address", "10.0.0.1")
            self.add_input_field("Gateway", "10.0.0.254")

    def add_input_field(self, label, default_value):
        """
        Adds a labeled input field to the dynamic configuration section.
        """
        input_field = QtWidgets.QLineEdit()
        input_field.setText(default_value)
        self.dynamic_input_layout.addRow(label, input_field)

    def apply_configuration(self):
        """
        Applies the configuration to the router based on user selection.
        """
        selected_ports = [port for port, button in self.port_buttons.items() if button.isChecked()]
        template_index = self.template_combo.currentIndex()
        input_values = [field.text() for field in self.dynamic_input_layout.findChildren(QtWidgets.QLineEdit)]

        # Perform the necessary configuration logic
        configuration_thread = ConfigurationThread(
            self.router, selected_ports, template_index, input_values
        )
        configuration_thread.configuration_result.connect(self.on_configuration_result)
        configuration_thread.start()

    def on_configuration_result(self, success, error_message):
        if success:
            QtWidgets.QMessageBox.information(self, "Success", "Configuration applied successfully.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to apply configuration: {error_message}")
    def setup_template_section(self):
        """
        Sets up the template selection section with styling.
        """
        templates_group = QtWidgets.QGroupBox("Configuration Templates")
        templates_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #9E9E9E;
                margin-top: 20px;
                background-color: #3C3C3C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #FFFFFF;
                font-size: 18px;
            }
        """)

        templates_layout = QtWidgets.QVBoxLayout()
        templates_group.setLayout(templates_layout)

        # Lista dostępnych szablonów
        self.templates = [
            "dhcp_server: Configure the router as a DHCP server.",
            "lan_dhcp: Configure LAN DHCP settings.",
            "data_configuration_without_bridge: Apply data configurations without bridging."
        ]

        # ComboBox do wyboru szablonu
        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: #5F5F5F;
                border: 1px solid #9E9E9E;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
            }
            QComboBox:hover {
                background-color: #6F6F6F;
                border-color: #4CAF50;
            }
            QComboBox:focus {
                border-color: #4CAF50;
            }
        """)

        # Dodajemy tylko nazwę szablonu do ComboBox
        template_names = [template.split(":")[0] for template in self.templates]
        self.template_combo.addItems(template_names)
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        templates_layout.addWidget(self.template_combo, stretch=1)

        # Etykieta wyświetlająca opis szablonu bezpośrednio pod dropdownem
        self.template_description = QtWidgets.QLabel()
        self.template_description.setWordWrap(True)
        self.template_description.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        templates_layout.addWidget(self.template_description, stretch=1)

        # Dynamiczne pola wejściowe na podstawie wybranego szablonu
        self.dynamic_input_group = QtWidgets.QGroupBox("Configuration Parameters")
        self.dynamic_input_group.setStyleSheet("""
            QGroupBox {
                background-color: #3C3C3C;
                border: 1px solid #9E9E9E;
            }
            QGroupBox::title {
                color: #FFFFFF;
                font-size: 16px;
            }
        """)

        self.dynamic_input_layout = QtWidgets.QFormLayout()
        self.dynamic_input_group.setLayout(self.dynamic_input_layout)
        templates_layout.addWidget(self.dynamic_input_group, stretch=8)

        self.main_layout.addWidget(templates_group, stretch=11)  # Pozostałe 55% zakładając total stretch=20

        # Inicjalizacja inputów dla pierwszego szablonu
        self.on_template_changed(0)
