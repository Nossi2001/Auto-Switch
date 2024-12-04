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
        layout = QtWidgets.QVBoxLayout()

        # Przycisk "Wpisz ręcznie"
        manual_button = QtWidgets.QPushButton("Wpisz ręcznie")
        manual_button.clicked.connect(self.open_manual_login)
        layout.addWidget(manual_button)

        # Przycisk "Znajdź urządzenia w sieci"
        auto_find_button = QtWidgets.QPushButton("Znajdź urządzenia w sieci")
        auto_find_button.clicked.connect(self.auto_find_devices)
        layout.addWidget(auto_find_button)

        self.setLayout(layout)

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
