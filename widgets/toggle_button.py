# toggle_button.py

from PyQt6 import QtWidgets, QtCore

class ToggleButton(QtWidgets.QToolButton):
    """
    Niestandardowy przycisk, który działa jako toggleable button z możliwością zmiany rozmiaru podczas hover.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setText('')
        # Ustawienie proporcji 2:1 (szerokość:wysokość)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(100)
        self.setMinimumHeight(50)
        self.setMaximumHeight(100)  # Maksymalna wysokość, aby przyciski nie rozciągały się zbyt wysoko

        self.setStyleSheet("""
            QToolButton {
                background-color: #FFFFFF;
                border: 2px solid #9E9E9E;
                border-radius: 5px;
            }
            QToolButton:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
            }
            QToolButton:hover {
                border: 2px solid #4CAF50;
            }
        """)
        # Animacja rozmiaru
        self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

    def enterEvent(self, event):
        # Animacja zwiększenia rozmiaru przycisku podczas hover
        self.animation.stop()
        current_geometry = self.geometry()
        new_geometry = QtCore.QRect(
            current_geometry.x() - 5,
            current_geometry.y() - 2.5,
            current_geometry.width() + 10,
            current_geometry.height() + 5
        )
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(new_geometry)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Animacja przywrócenia rozmiaru przycisku po zakończeniu hover
        self.animation.stop()
        current_geometry = self.geometry()
        original_geometry = QtCore.QRect(
            current_geometry.x() + 5,
            current_geometry.y() + 2.5,
            current_geometry.width() - 10,
            current_geometry.height() - 5
        )
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(original_geometry)
        self.animation.start()
        super().leaveEvent(event)
