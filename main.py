import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QListWidget, QPushButton,
    QVBoxLayout, QLineEdit, QMessageBox, QStackedWidget, QHBoxLayout
)

from PyQt6.QtCore import Qt
from Auto_Finder_Router import Auto_Finder_Router
from open_wrt_router import OpenWrtRouter  # Import klasy OpenWrtRouter

class RouterConfigurator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.stacked_widget = QStackedWidget()

        # Strona 0: Ekran powitalny z przyciskiem "Skanuj"
        self.page_scan = QWidget()
        self.page_scan_layout = QVBoxLayout()

        self.scan_label = QLabel('Kliknij "Skanuj", aby wyszukać urządzenia w sieci.')
        self.scan_button = QPushButton('Skanuj')
        self.scan_button.clicked.connect(self.scan_network)

        self.page_scan_layout.addWidget(self.scan_label)
        self.page_scan_layout.addWidget(self.scan_button)
        self.page_scan.setLayout(self.page_scan_layout)

        # Strona 1: Lista znalezionych urządzeń
        self.page_select = QWidget()
        self.page_select_layout = QVBoxLayout()

        self.device_list_label = QLabel('Znalezione urządzenia:')
        self.device_list_widget = QListWidget()

        self.select_button = QPushButton('Wybierz')
        self.select_button.clicked.connect(self.select_device)

        self.page_select_layout.addWidget(self.device_list_label)
        self.page_select_layout.addWidget(self.device_list_widget)
        self.page_select_layout.addWidget(self.select_button)
        self.page_select.setLayout(self.page_select_layout)

        # Strona 2: Formularz logowania
        self.page_login = QWidget()
        self.page_login_layout = QVBoxLayout()

        self.login_info_label = QLabel('Zaloguj się do routera:')
        self.username_label = QLabel('Nazwa użytkownika:')
        self.username_input = QLineEdit()
        self.password_label = QLabel('Hasło:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton('Zaloguj')
        self.login_button.clicked.connect(self.login_to_router)

        self.page_login_layout.addWidget(self.login_info_label)
        self.page_login_layout.addWidget(self.username_label)
        self.page_login_layout.addWidget(self.username_input)
        self.page_login_layout.addWidget(self.password_label)
        self.page_login_layout.addWidget(self.password_input)
        self.page_login_layout.addWidget(self.login_button)
        self.page_login.setLayout(self.page_login_layout)

        # Strona 3: Zmiana IP i przyciski
        self.page_configure = QWidget()
        self.page_configure_layout = QVBoxLayout()

        self.ip_label = QLabel('Nowe IP:')
        self.ip_input = QLineEdit()

        # Przyciski: Zastosuj, Backup, Wyjdź
        self.buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton('Zastosuj')
        self.apply_button.clicked.connect(self.apply_new_ip)
        self.backup_button = QPushButton('Backup')
        self.backup_button.clicked.connect(self.backup_configuration)
        self.exit_button = QPushButton('Wyjdź')
        self.exit_button.clicked.connect(self.exit_application)

        self.buttons_layout.addWidget(self.apply_button)
        self.buttons_layout.addWidget(self.backup_button)
        self.buttons_layout.addWidget(self.exit_button)

        self.page_configure_layout.addWidget(self.ip_label)
        self.page_configure_layout.addWidget(self.ip_input)
        self.page_configure_layout.addLayout(self.buttons_layout)
        self.page_configure.setLayout(self.page_configure_layout)

        # Dodanie stron do QStackedWidget
        self.stacked_widget.addWidget(self.page_scan)       # Indeks 0
        self.stacked_widget.addWidget(self.page_select)     # Indeks 1
        self.stacked_widget.addWidget(self.page_login)      # Indeks 2
        self.stacked_widget.addWidget(self.page_configure)  # Indeks 3

        # Ustawienie głównego układu
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)
        self.setWindowTitle('Router Configurator')
        self.show()

    def scan_network(self):
        # Przejście do strony z listą urządzeń
        self.stacked_widget.setCurrentIndex(1)

        self.device_list_widget.clear()
        self.device_list_widget.addItem('Skanowanie sieci, proszę czekać...')
        QApplication.processEvents()  # Aktualizacja GUI
        self.devices = Auto_Finder_Router()
        self.device_list_widget.clear()
        if self.devices:
            for device in self.devices:
                item_text = f"IP: {device['ip']}, MAC: {device['mac']}, Producent: {device['vendor']}"
                self.device_list_widget.addItem(item_text)
        else:
            self.device_list_widget.addItem('Nie znaleziono urządzeń.')

    def select_device(self):
        selected_items = self.device_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Brak wyboru', 'Proszę wybrać urządzenie z listy.')
            return
        item = selected_items[0]
        index = self.device_list_widget.row(item)
        device = self.devices[index]
        self.selected_device = device  # Zapisujemy wybrane urządzenie

        # Przejście do strony logowania
        self.stacked_widget.setCurrentIndex(2)

    def login_to_router(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Błąd', 'Proszę wprowadzić nazwę użytkownika i hasło.')
            return

        router_ip = self.selected_device['ip']
        self.router = OpenWrtRouter(ip=router_ip, username=username, password=password)

        if self.router.connect():
            QMessageBox.information(self, 'Sukces', f'Zalogowano do routera {router_ip}.')
            # Przejście do strony konfiguracji
            self.stacked_widget.setCurrentIndex(3)
        else:
            QMessageBox.critical(self, 'Błąd', f'Nie udało się zalogować do routera {router_ip}.')

    def apply_new_ip(self):
        new_ip = self.ip_input.text()
        if not new_ip:
            QMessageBox.warning(self, 'Błąd', 'Proszę wprowadzić nowy adres IP.')
            return

        if self.router:
            if self.router.change_ip(new_ip):
                QMessageBox.information(self, 'Sukces', f'Adres IP został zmieniony na {new_ip}.')
            else:
                QMessageBox.critical(self, 'Błąd', 'Nie udało się zmienić adresu IP.')
        else:
            QMessageBox.critical(self, 'Błąd', 'Brak połączenia z routerem.')

    def backup_configuration(self):
        if self.router:
            if self.router.backup_configuration():
                QMessageBox.information(self, 'Sukces', 'Kopia zapasowa została utworzona.')
            else:
                QMessageBox.critical(self, 'Błąd', 'Nie udało się utworzyć kopii zapasowej.')
        else:
            QMessageBox.critical(self, 'Błąd', 'Brak połączenia z routerem.')

    def exit_application(self):
        # Rozłączamy się z routerem, jeśli połączenie istnieje
        if hasattr(self, 'router') and self.router:
            self.router.disconnect()
        # Zamykamy aplikację
        self.close()

    def closeEvent(self, event):
        # Nadpisujemy metodę zamykającą okno, aby upewnić się, że połączenie jest zamknięte
        if hasattr(self, 'router') and self.router:
            self.router.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RouterConfigurator()
    sys.exit(app.exec())
