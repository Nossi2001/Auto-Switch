from PyQt6 import QtWidgets, QtCore
from utils.ui_helpers import set_window_size_percentage

class DeviceListPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        set_window_size_percentage(self)  # Ustawienie rozmiaru okna
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Centrujemy całą stronę

        # Nagłówek
        header_label = QtWidgets.QLabel("Wybierz urządzenie")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(header_label)

        # Lista urządzeń
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setStyleSheet("font-size: 16px; padding: 10px; width: 90%;")  # Stylowanie listy
        layout.addWidget(self.list_widget)

        # Przycisk "Połącz"
        connect_button = QtWidgets.QPushButton("Połącz")
        connect_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px; font-size: 18px; border-radius: 5px; margin-top: 20px;")
        connect_button.clicked.connect(self.connect_to_device)
        layout.addWidget(connect_button)

        # Przycisk powrotu
        back_button = QtWidgets.QPushButton("Wróć")
        back_button.setStyleSheet("background-color: #f44336; color: white; padding: 15px; font-size: 18px; border-radius: 5px;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def update_device_list(self, devices):
        self.list_widget.clear()
        for device in devices:
            item_text = f"{device['ip']} - {device['vendor']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, device)
            self.list_widget.addItem(item)

    def connect_to_device(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            device = item.data(QtCore.Qt.ItemDataRole.UserRole)
            ip = device['ip']

            # Przejdź do ConnectPage z wybranym IP
            connect_page = self.stacked_widget.widget(3)
            connect_page.set_device_ip(ip)
            self.stacked_widget.setCurrentIndex(3)
        else:
            QtWidgets.QMessageBox.warning(self, "Brak wyboru", "Nie wybrano żadnego urządzenia.")

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)  # Powrót do StartPage
