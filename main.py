# main.py

import sys
from PyQt6 import QtWidgets
from pages.start_page import StartPage
from pages.manual_login_page import ManualLoginPage
from pages.device_list_page import DeviceListPage
from pages.connect_page import ConnectPage
from pages.router_configurator_page import RouterConfiguratorPage
from utils.ui_helpers import set_window_size_percentage

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Router Configurator")
        set_window_size_percentage(self)

        # Ustawienie centralnego widgetu jako QStackedWidget
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Dodanie stron do QStackedWidget
        self.start_page = StartPage(self.stacked_widget)
        self.manual_login_page = ManualLoginPage(self.stacked_widget)
        self.device_list_page = DeviceListPage(self.stacked_widget)
        self.connect_page = ConnectPage(self.stacked_widget)
        self.router_configurator_page = RouterConfiguratorPage(self.stacked_widget)

        self.stacked_widget.addWidget(self.start_page)                   # Index 0
        self.stacked_widget.addWidget(self.manual_login_page)            # Index 1
        self.stacked_widget.addWidget(self.device_list_page)             # Index 2
        self.stacked_widget.addWidget(self.connect_page)                 # Index 3
        self.stacked_widget.addWidget(self.router_configurator_page)     # Index 4

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
