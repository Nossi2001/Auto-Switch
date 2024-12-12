# widgets/custom_widgets.py

from PyQt6 import QtWidgets
from PyQt6.QtGui import QColor

def adjust_color(hex_color, factor=0.1):
    """Adjust the brightness of a hex color."""
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2],16) for i in (0,2,4)]
    luminance = 0.299*r + 0.587*g + 0.114*b
    if luminance > 128:
        # Make it slightly darker
        r = max(int(r * (1 - factor)), 0)
        g = max(int(g * (1 - factor)), 0)
        b = max(int(b * (1 - factor)), 0)
    else:
        # Make it slightly lighter
        r = min(int(r + (255 - r) * factor), 255)
        g = min(int(g + (255 - g) * factor), 255)
        b = min(int(b + (255 - b) * factor), 255)
    return f"#{r:02X}{g:02X}{b:02X}"

def validate_color(c):
    """Validate if the color string is in #RRGGBB format."""
    if isinstance(c, str) and c.startswith('#') and len(c) == 7:
        try:
            int(c[1:], 16)
            return True
        except ValueError:
            return False
    return False

class PortButton(QtWidgets.QPushButton):
    def __init__(self, label=''):
        super().__init__(label)
        self.setCheckable(True)
        self.current_color = '#5F5F5F'
        self.hover_color = adjust_color(self.current_color, factor=0.1)
        self.checked_color = adjust_color(self.current_color, factor=0.2)
        self.update_style()

        # Change color on hover
        self.setMouseTracking(True)
        self.enterEvent = self.on_hover_enter
        self.leaveEvent = self.on_hover_leave

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                border: 2px solid #9E9E9E;
                border-radius: 5px;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
                border-color: #4CAF50;
            }}
            QPushButton:checked {{
                background-color: {self.checked_color};
                border-color: #388E3C;
            }}
        """)

    def set_color(self, color):
        """Set the button color."""
        if validate_color(color):  # Sprawdzenie, czy kolor jest poprawny
            self.current_color = color
            self.hover_color = adjust_color(color, factor=0.1)
            self.checked_color = adjust_color(color, factor=0.2)
            self.update_style()

    def on_hover_enter(self, event):
        pass  # Style is handled via stylesheet

    def on_hover_leave(self, event):
        pass  # Style is handled via stylesheet

class VLANLegend(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.existing_vlans = set()  # Przechowuje istniejące VLAN IDs
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #3C3C3C;
                border: 1px solid #9E9E9E;
                border-radius: 5px;
            }
        """)

    def add_vlan(self, vlan_id, vlan_name, color):
        if vlan_id in self.existing_vlans:
            return  # Pomijamy powtórzenie VLAN-u

        vlan_widget = QtWidgets.QWidget()
        vlan_layout = QtWidgets.QHBoxLayout()
        vlan_widget.setLayout(vlan_layout)

        color_label = QtWidgets.QLabel("   ")
        color_label.setFixedSize(20, 20)
        color_label.setStyleSheet(f"background-color: {color}; border: 1px solid #FFFFFF;")
        vlan_layout.addWidget(color_label)

        text_label = QtWidgets.QLabel(f" VLAN {vlan_id}: {vlan_name}")
        vlan_layout.addWidget(text_label)

        self.layout.addWidget(vlan_widget)
        self.existing_vlans.add(vlan_id)  # Dodajemy VLAN ID do istniejących

    def clear_legends(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.existing_vlans.clear()  # Czyścimy istniejące VLAN IDs
