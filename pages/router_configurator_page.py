# pages/router_configurator_page.py

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
        self.clear_layout(self.dynamic_input_layout)

        # Create inputs based on the selected template
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
            # Informational label
            info_label = QtWidgets.QLabel("LAN DHCP configuration will be applied to the selected ports.")
            info_label.setWordWrap(True)
            self.dynamic_input_layout.addRow(info_label)

        elif selected_template == "data_configuration_without_bridge":
            # Informational label
            info_label = QtWidgets.QLabel("Data configuration without bridge will be applied to the selected ports.")
            info_label.setWordWrap(True)
            self.dynamic_input_layout.addRow(info_label)

    def apply_configuration(self):
        selected_template_index = self.template_combo.currentIndex()
        selected_template = self.templates[selected_template_index].split(":")[0]

        # List of selected ports for configuration (use tooltips instead of labels)
        selected_ports = [btn.toolTip() for btn in self.port_buttons.values() if btn.isChecked()]

        # Validate template selection
        if not selected_template:
            QtWidgets.QMessageBox.warning(self, "Error", "No configuration template selected.")
            return

        # Validate port selection
        if not selected_ports:
            QtWidgets.QMessageBox.warning(self, "No Ports Selected", "No ports selected for configuration.")
            return

        # Get dynamic inputs based on the selected template
        config_params = {}
        if selected_template == "dhcp_server":
            name_server = self.name_server_input.text()
            gateway = self.gateway_input.text()
            netmask = self.netmask_input.text()
            dhcp_range = self.dhcp_range_input.text()

            if not name_server or not gateway or not netmask or not dhcp_range:
                QtWidgets.QMessageBox.warning(self, "Error", "All fields are required for DHCP Server configuration.")
                return

            # Split dhcp_range_start and dhcp_range_stop
            try:
                dhcp_range_start, dhcp_range_stop = dhcp_range.split()
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "Error", "DHCP Range must contain two addresses separated by a space.")
                return

            config_params = {
                "name_server": name_server,
                "gateway": gateway,
                "netmask": netmask,
                "dhcp_range_start": dhcp_range_start,
                "dhcp_range_stop": dhcp_range_stop
            }

        elif selected_template == "lan_dhcp":
            # No additional parameters required
            config_params = {
                "ports": selected_ports
            }

        elif selected_template == "data_configuration_without_bridge":
            # No additional parameters required
            config_params = {
                "ports": selected_ports
            }

        # Disable the interface
        self.setEnabled(False)

        # Start configuration in a separate thread
        self.configuration_thread = ConfigurationThread(
            self.router,
            selected_template,
            selected_ports,
            config_params  # Pass additional parameters
        )
        self.configuration_thread.configuration_result.connect(self.on_configuration_result)
        self.configuration_thread.start()

    def on_configuration_result(self, success, message):
        # Re-enable the interface
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
