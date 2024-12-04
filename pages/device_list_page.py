# pages/device_list_page.py

from PyQt6 import QtWidgets, QtCore

class DeviceListPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Lista urządzeń
        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        # Przycisk "Połącz"
        connect_button = QtWidgets.QPushButton("Połącz")
        connect_button.clicked.connect(self.connect_to_device)
        layout.addWidget(connect_button)

        # Przycisk powrotu
        back_button = QtWidgets.QPushButton("Wróć")
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
