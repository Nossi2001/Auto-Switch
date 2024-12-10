# pages/start_page.py

from PyQt6 import QtWidgets, QtCore
from config import Cisco_Router, Cisco_Switch

class StartPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.go_to_config_page = None

        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
                font-family: Arial;
            }
            QRadioButton {
                font-size:16px;
                color:#FFFFFF;
            }
            QPushButton {
                background-color:#5F5F5F;
                border:2px solid #9E9E9E;
                border-radius:5px;
                color:#FFFFFF;
                font-size:16px;
                padding:5px 10px;
            }
            QPushButton:hover {
                border-color:#4CAF50;
                background-color:#6F6F6F;
            }
        """)

        self.device_type = 'router'
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        title_label = QtWidgets.QLabel("Wybierz typ urządzenia i model")
        title_label.setStyleSheet("font-size:20px;font-weight:bold;")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        type_layout = QtWidgets.QHBoxLayout()
        self.router_radio = QtWidgets.QRadioButton("Router")
        self.router_radio.setChecked(True)
        self.switch_radio = QtWidgets.QRadioButton("Switch")

        self.router_radio.toggled.connect(self.on_type_change)

        type_layout.addWidget(self.router_radio)
        type_layout.addWidget(self.switch_radio)
        layout.addLayout(type_layout)

        self.device_group = QtWidgets.QGroupBox("Urządzenia")
        self.device_layout = QtWidgets.QVBoxLayout()
        self.device_group.setLayout(self.device_layout)
        layout.addWidget(self.device_group)

        self.load_devices()

        next_button = QtWidgets.QPushButton("Dalej")
        next_button.clicked.connect(self.go_next)
        layout.addWidget(next_button)

        self.setLayout(layout)

    def on_type_change(self):
        if self.router_radio.isChecked():
            self.device_type = 'router'
        else:
            self.device_type = 'switch'
        self.load_devices()

    def load_devices(self):
        while self.device_layout.count():
            item = self.device_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        devices = Cisco_Router if self.device_type == 'router' else Cisco_Switch
        self.device_buttons = []
        for d in devices.keys():
            rb = QtWidgets.QRadioButton(d)
            self.device_layout.addWidget(rb)
            self.device_buttons.append(rb)

        if self.device_buttons:
            self.device_buttons[0].setChecked(True)

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
