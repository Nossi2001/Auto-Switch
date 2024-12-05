# pages/start_page.py

from PyQt6 import QtWidgets, QtCore
from threads.scan_thread import ScanThread
from Auto_Finder_Router import Auto_Finder_Router
from utils.ui_helpers import set_window_size_percentage

class StartPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        set_window_size_percentage(self)  # Ustawienie rozmiaru okna
        self.init_ui()

    def init_ui(self):
        # Ustawienie stylów CSS
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 26px;
                color: #333;
                text-align: center;
                padding-top: 50px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                padding: 20px;
                margin: 10px;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            QPushButton:hover {
                background-color: #45a049;
                transform: scale(1.05);  /* Animacja powiększenia przy najechaniu */
            }
            QHBoxLayout {
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
            }
        """)

        # Layout główny
        main_layout = QtWidgets.QVBoxLayout()

        # Tytuł strony - tekst wyśrodkowany
        self.title_label = QtWidgets.QLabel("Wybierz opcję")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Layout na przyciski (poziomo, z centrowaniem)
        button_layout = QtWidgets.QHBoxLayout()

        # Przycisk "Wpisz ręcznie"
        manual_button = QtWidgets.QPushButton("Wpisz ręcznie")
        manual_button.clicked.connect(self.open_manual_login)
        button_layout.addWidget(manual_button)

        # Przycisk "Znajdź urządzenia w sieci"
        auto_find_button = QtWidgets.QPushButton("Znajdź urządzenia w sieci")
        auto_find_button.clicked.connect(self.auto_find_devices)
        button_layout.addWidget(auto_find_button)

        # Dodanie layoutu przycisków do głównego layoutu
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def open_manual_login(self):
        self.stacked_widget.setCurrentIndex(1)  # Przejdź do ManualLoginPage

    def auto_find_devices(self):
        # Uruchom skanowanie w osobnym wątku, aby nie blokować GUI
        self.setEnabled(False)
        self.scan_thread = ScanThread()
        self.scan_thread.scan_result.connect(self.on_scan_result)
        self.scan_thread.start()

    def on_scan_result(self, devices):
        self.setEnabled(True)
        if devices:
            # Przejdź do DeviceListPage z listą urządzeń
            device_list_page = self.stacked_widget.widget(2)
            device_list_page.update_device_list(devices)
            self.stacked_widget.setCurrentIndex(2)
        else:
            QtWidgets.QMessageBox.information(self, "Skanowanie zakończone", "Nie znaleziono żadnych urządzeń.")
