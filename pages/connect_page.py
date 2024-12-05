from PyQt6 import QtWidgets, QtCore
from threads.connection_thread import ConnectionThread
from utils.ui_helpers import set_window_size_percentage

class ConnectPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.device_ip = None
        set_window_size_percentage(self)  # Ustawienie rozmiaru okna
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Centrujemy całą stronę

        # Nagłówek
        header_label = QtWidgets.QLabel("Łączenie z urządzeniem")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(header_label)

        # Informacja o wybranym urządzeniu
        self.info_label = QtWidgets.QLabel("Łączenie z urządzeniem:")
        self.info_label.setStyleSheet("font-size: 18px; color: #777; margin-top: 20px;")
        layout.addWidget(self.info_label)

        # Pole do wprowadzania nazwy użytkownika
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        self.username_input.setText("user")  # Domyślna nazwa użytkownika
        self.username_input.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.username_input)

        # Pole do wprowadzania hasła
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_input.setText("user")  # Domyślne hasło
        self.password_input.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.password_input)

        # Przycisk połączenia
        connect_button = QtWidgets.QPushButton("Połącz")
        connect_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px; font-size: 18px; border-radius: 5px;")
        connect_button.clicked.connect(self.handle_connect)
        layout.addWidget(connect_button)

        # Przycisk powrotu
        back_button = QtWidgets.QPushButton("Wróć")
        back_button.setStyleSheet("background-color: #f44336; color: white; padding: 15px; font-size: 18px; border-radius: 5px;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def set_device_ip(self, ip):
        self.device_ip = ip
        self.info_label.setText(f"Łączenie z {self.device_ip}")

    def handle_connect(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Wszystkie pola są wymagane.")
            return

        # Zablokuj okno połączenia
        self.setEnabled(False)

        # Uruchom połączenie w osobnym wątku
        self.connection_thread = ConnectionThread(self.device_ip, username, password)
        self.connection_thread.connection_result.connect(self.on_connection_result)
        self.connection_thread.start()

    def on_connection_result(self, success, error_message):
        # Odblokuj okno połączenia
        self.setEnabled(True)

        if success:
            # Przejście do głównego okna aplikacji
            configurator_page = self.stacked_widget.widget(4)
            configurator_page.initialize(self.device_ip,
                                         self.username_input.text(),
                                         self.password_input.text())
            self.stacked_widget.setCurrentIndex(4)
        else:
            QtWidgets.QMessageBox.critical(self, "Błąd", f"Nie udało się połączyć z urządzeniem:\n{error_message}")

    def go_back(self):
        self.stacked_widget.setCurrentIndex(2)  # Powrót do DeviceListPage
