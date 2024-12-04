# pages/manual_login_page.py

from PyQt6 import QtWidgets, QtCore
from threads.connection_thread import ConnectionThread

class ManualLoginPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Pole do wprowadzania adresu IP
        self.ip_input = QtWidgets.QLineEdit()
        self.ip_input.setPlaceholderText("Adres IP")
        self.ip_input.setText("192.168.55.50")  # Domyślny IP
        layout.addWidget(self.ip_input)

        # Pole do wprowadzania nazwy użytkownika
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        self.username_input.setText("user")  # Domyślna nazwa użytkownika
        layout.addWidget(self.username_input)

        # Pole do wprowadzania hasła
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_input.setText("user")  # Domyślne hasło
        layout.addWidget(self.password_input)

        # Przycisk logowania
        login_button = QtWidgets.QPushButton("Zaloguj")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        # Przycisk powrotu
        back_button = QtWidgets.QPushButton("Wróć")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def handle_login(self):
        ip = self.ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        if not ip or not username or not password:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Wszystkie pola są wymagane.")
            return

        # Zablokuj okno logowania
        self.setEnabled(False)

        # Uruchom połączenie w osobnym wątku
        self.connection_thread = ConnectionThread(ip, username, password)
        self.connection_thread.connection_result.connect(self.on_connection_result)
        self.connection_thread.start()

    def on_connection_result(self, success, error_message):
        # Odblokuj okno logowania
        self.setEnabled(True)

        if success:
            # Przejście do głównego okna aplikacji
            configurator_page = self.stacked_widget.widget(4)
            configurator_page.initialize(self.ip_input.text(),
                                         self.username_input.text(),
                                         self.password_input.text())
            self.stacked_widget.setCurrentIndex(4)
        else:
            QtWidgets.QMessageBox.critical(self, "Błąd", f"Nie udało się połączyć z routerem:\n{error_message}")

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)  # Powrót do StartPage
