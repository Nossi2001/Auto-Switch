from PyQt6 import QtWidgets, QtCore
from config import Cisco_Router, Cisco_Switch
from styles import BASE_STYLE, GROUPBOX_STYLE

class StartPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.go_to_config_page = None
        self.device_descriptions = {}

        self.setStyleSheet(BASE_STYLE + """
            QPushButton[device-button="true"] {
                border: 3px solid #3D3D3D;
                padding: 15px;
                margin: 5px;
                border-radius: 6px;
            }
            QPushButton[device-button="true"]:checked {
                background-color: #4D4D4D;
                border: 3px solid #4CAF50;
            }
        """)

        self.device_type = 'router'
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins

        title_label = QtWidgets.QLabel("Wybierz typ urządzenia i model")
        title_label.setProperty("heading", "true")
        layout.addWidget(title_label)

        type_layout = QtWidgets.QHBoxLayout()
        self.router_radio = QtWidgets.QPushButton("Router")
        self.router_radio.setCheckable(True)
        self.router_radio.setChecked(True)  # Preselect router
        self.switch_radio = QtWidgets.QPushButton("Switch")
        self.switch_radio.setCheckable(True)
        
        self.router_radio.clicked.connect(lambda: self.on_type_change())
        self.switch_radio.clicked.connect(lambda: self.on_type_change())

        type_layout.addWidget(self.router_radio)
        type_layout.addWidget(self.switch_radio)
        layout.addLayout(type_layout)

        self.device_group = QtWidgets.QWidget()
        self.device_layout = QtWidgets.QVBoxLayout()
        self.device_group.setLayout(self.device_layout)
        layout.addWidget(self.device_group)

        self.load_devices()

        next_button = QtWidgets.QPushButton("Dalej")
        next_button.clicked.connect(self.go_next)
        layout.addWidget(next_button)

        self.setLayout(layout)

    def on_type_change(self):
        if self.sender() == self.router_radio:
            self.router_radio.setChecked(True)
            self.switch_radio.setChecked(False)
            self.device_type = 'router'
        else:
            self.router_radio.setChecked(False)
            self.switch_radio.setChecked(True)
            self.device_type = 'switch'
        self.load_devices()

    def load_devices(self):
        # Clear existing buttons
        while self.device_layout.count():
            item = self.device_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        devices = Cisco_Router if self.device_type == 'router' else Cisco_Switch
        self.device_buttons = []
        for d in devices.keys():
            # Store description for the device
            self.device_descriptions[d] = devices[d]['description']
            
            rb = QtWidgets.QPushButton(d)
            rb.setCheckable(True)
            # Set tooltip with device description
            rb.setToolTip(devices[d]['description'])  # Tooltip will stay visible until mouse moves away
            rb.setProperty("device-button", "true")
            rb.setStyleSheet("border-radius: 6px;")
            self.device_layout.addWidget(rb)
            self.device_buttons.append(rb)
            rb.clicked.connect(lambda checked, btn=rb: self.on_device_selected(btn))

    def on_device_selected(self, clicked_button):
        # Uncheck all other buttons
        for button in self.device_buttons:
            if button != clicked_button:
                button.setChecked(False)
        # Ensure the clicked button is checked
        clicked_button.setChecked(True)

    def go_next(self):
        selected_device = None
        for rb in self.device_buttons:
            if rb.isChecked():
                selected_device = rb.text()
                break

        if selected_device and self.go_to_config_page:
            self.go_to_config_page(self.device_type, selected_device)
        else:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Wybierz urządzenie zanim przejdziesz dalej.")
