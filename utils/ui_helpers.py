# utils/ui_helpers.py

from PyQt6 import QtWidgets

def set_window_size_percentage(window, width_pct=0.8, height_pct=0.8):
    screen = QtWidgets.QApplication.primaryScreen()
    screen_size = screen.size()
    width = int(screen_size.width() * width_pct)
    height = int(screen_size.height() * height_pct)
    window.resize(width, height)
