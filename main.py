# edge_router_gui.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from edge_router import EdgeRouter

class EdgeRouterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.router = None

    def init_ui(self):
        self.setWindowTitle('EdgeRouter Configuration')

        # Dane logowania
        self.ip_label = QLabel('Router IP:')
        self.ip_input = QLineEdit('192.168.55.50')
        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit('user')
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit('user')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Przyciski połączenia
        self.connect_button = QPushButton('Connect')
        self.disconnect_button = QPushButton('Disconnect')
        self.disconnect_button.setEnabled(False)

        # Pola konfiguracji VLAN
        self.vlan_id_label = QLabel('VLAN ID:')
        self.vlan_id_input = QLineEdit()
        self.parent_interface_label = QLabel('Parent Interface:')
        self.parent_interface_input = QLineEdit('eth1')
        self.vlan_address_label = QLabel('VLAN Address:')
        self.vlan_address_input = QLineEdit('192.168.100.1/24')
        self.vlan_description_label = QLabel('VLAN Description:')
        self.vlan_description_input = QLineEdit('Interfejs VLAN 100')
        self.create_vlan_button = QPushButton('Create VLAN Interface')
        self.create_vlan_button.setEnabled(False)

        # Pola konfiguracji portu dostępu
        self.access_interface_label = QLabel('Access Interface:')
        self.access_interface_input = QLineEdit('eth2')
        self.access_vlan_id_label = QLabel('Access VLAN ID:')
        self.access_vlan_id_input = QLineEdit()
        self.configure_access_button = QPushButton('Configure Access Port')
        self.configure_access_button.setEnabled(False)

        # Pola konfiguracji portu trunk
        self.trunk_interface_label = QLabel('Trunk Interface:')
        self.trunk_interface_input = QLineEdit('eth3')
        self.allowed_vlans_label = QLabel('Allowed VLANs (comma-separated):')
        self.allowed_vlans_input = QLineEdit('100,200,300')
        self.configure_trunk_button = QPushButton('Configure Trunk Port')
        self.configure_trunk_button.setEnabled(False)

        # Pole logów
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Układ interfejsu
        layout = QVBoxLayout()

        # Dane logowania
        login_layout = QHBoxLayout()
        login_layout.addWidget(self.ip_label)
        login_layout.addWidget(self.ip_input)
        login_layout.addWidget(self.username_label)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_label)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.connect_button)
        login_layout.addWidget(self.disconnect_button)
        layout.addLayout(login_layout)

        # Konfiguracja VLAN
        vlan_layout = QHBoxLayout()
        vlan_layout.addWidget(self.vlan_id_label)
        vlan_layout.addWidget(self.vlan_id_input)
        vlan_layout.addWidget(self.parent_interface_label)
        vlan_layout.addWidget(self.parent_interface_input)
        vlan_layout.addWidget(self.vlan_address_label)
        vlan_layout.addWidget(self.vlan_address_input)
        vlan_layout.addWidget(self.vlan_description_label)
        vlan_layout.addWidget(self.vlan_description_input)
        vlan_layout.addWidget(self.create_vlan_button)
        layout.addLayout(vlan_layout)

        # Konfiguracja portu dostępu
        access_layout = QHBoxLayout()
        access_layout.addWidget(self.access_interface_label)
        access_layout.addWidget(self.access_interface_input)
        access_layout.addWidget(self.access_vlan_id_label)
        access_layout.addWidget(self.access_vlan_id_input)
        access_layout.addWidget(self.configure_access_button)
        layout.addLayout(access_layout)

        # Konfiguracja portu trunk
        trunk_layout = QHBoxLayout()
        trunk_layout.addWidget(self.trunk_interface_label)
        trunk_layout.addWidget(self.trunk_interface_input)
        trunk_layout.addWidget(self.allowed_vlans_label)
        trunk_layout.addWidget(self.allowed_vlans_input)
        trunk_layout.addWidget(self.configure_trunk_button)
        layout.addLayout(trunk_layout)

        # Pole logów
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # Połączenie sygnałów z metodami
        self.connect_button.clicked.connect(self.connect_to_router)
        self.disconnect_button.clicked.connect(self.disconnect_from_router)
        self.create_vlan_button.clicked.connect(self.create_vlan_interface)
        self.configure_access_button.clicked.connect(self.configure_access_port)
        self.configure_trunk_button.clicked.connect(self.configure_trunk_port)

    def log(self, message):
        self.log_output.append(message)

    def connect_to_router(self):
        ip = self.ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        self.router = EdgeRouter(ip=ip, username=username, password=password)
        if self.router.connect():
            self.log(f"Połączono z routerem {ip}.")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.create_vlan_button.setEnabled(True)
            self.configure_access_button.setEnabled(True)
            self.configure_trunk_button.setEnabled(True)
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się połączyć z routerem.")
            self.router = None

    def disconnect_from_router(self):
        if self.router:
            self.router.disconnect()
            self.log("Rozłączono z routerem.")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.create_vlan_button.setEnabled(False)
            self.configure_access_button.setEnabled(False)
            self.configure_trunk_button.setEnabled(False)
            self.router = None

    def create_vlan_interface(self):
        vlan_id = self.vlan_id_input.text()
        parent_interface = self.parent_interface_input.text()
        vlan_address = self.vlan_address_input.text()
        vlan_description = self.vlan_description_input.text()

        if not vlan_id.isdigit():
            QMessageBox.warning(self, "Błąd", "VLAN ID musi być liczbą całkowitą.")
            return

        if self.router.create_vlan_interface(parent_interface, vlan_id, address=vlan_address, description=vlan_description):
            self.log(f"Utworzono interfejs VLAN {vlan_id} na {parent_interface}.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się utworzyć interfejsu VLAN.")

    def configure_access_port(self):
        interface_name = self.access_interface_input.text()
        vlan_id = self.access_vlan_id_input.text()

        if not vlan_id.isdigit():
            QMessageBox.warning(self, "Błąd", "VLAN ID musi być liczbą całkowitą.")
            return

        if self.router.configure_access_port(interface_name, vlan_id):
            self.log(f"Skonfigurowano {interface_name} jako port dostępu dla VLAN {vlan_id}.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się skonfigurować portu dostępu.")

    def configure_trunk_port(self):
        interface_name = self.trunk_interface_input.text()
        vlan_list = self.allowed_vlans_input.text()

        try:
            allowed_vlans = [int(v.strip()) for v in vlan_list.split(',') if v.strip().isdigit()]
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Lista VLAN-ów musi zawierać liczby całkowite, oddzielone przecinkami.")
            return

        if not allowed_vlans:
            QMessageBox.warning(self, "Błąd", "Musisz podać przynajmniej jeden VLAN ID.")
            return

        if self.router.configure_trunk_port(interface_name, allowed_vlans):
            vlan_str = ', '.join(map(str, allowed_vlans))
            self.log(f"Skonfigurowano {interface_name} jako port trunk dla VLAN-ów {vlan_str}.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się skonfigurować portu trunk.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = EdgeRouterGUI()
    gui.show()
    sys.exit(app.exec())
