# main.py
import sys
from PyQt6 import QtWidgets
from pages.start_page import StartPage
from pages.config_page import ConfigPage

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Set the application-wide style sheet
    app.setStyleSheet("QMainWindow { background-color: #2B2B2B; }")
    
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Konfigurator Urządzeń Sieciowych")

    stacked_widget = QtWidgets.QStackedWidget()
    main_window.setCentralWidget(stacked_widget)

    start_page = StartPage(stacked_widget)
    config_page = ConfigPage(stacked_widget)

    stacked_widget.addWidget(start_page)   # Index 0
    stacked_widget.addWidget(config_page)  # Index 1

    def go_to_config_page(device_type, device_name):
        config_page.initialize(device_type, device_name)
        stacked_widget.setCurrentIndex(1)

    start_page.go_to_config_page = go_to_config_page

    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
