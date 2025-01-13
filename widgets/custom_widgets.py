# widgets/custom_widgets.py

from PyQt6 import QtWidgets
from PyQt6 import QtGui
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
        self.vlan_color = None  # Store the VLAN color
        self.setFixedSize(100, 40)
        self.setCheckable(True)
        self.current_color = '#5F5F5F'
        self.background_color = '#5F5F5F'
        self.hover_color = adjust_color(self.current_color, factor=0.1)
        self.checked_color = adjust_color(self.current_color, factor=0.2)
        self.setFont(QtGui.QFont('Segoe UI', 10))
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid #3D3D3D;
                background-color: {self.background_color};
                border-radius: 4px;
                color: white;
                padding: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
                border: 2px solid #4CAF50;
            }}
            QPushButton:checked {{
                background-color: {self.checked_color};
                border: 3px solid #4CAF50;
                font-weight: bold;
            }}
        """)

    def set_color(self, color):
        """Set the button color."""
        if validate_color(color):  # Check if the color is valid
            self.vlan_color = color  # Store the VLAN color
            self.background_color = color
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
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.existing_vlans = set()  # Stores existing VLAN IDs
        self.current_row = 0
        self.current_col = 0
        self.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #E0E0E0;
                padding: 2px;
                margin: 1px;
            }
            QWidget {
                background-color: #2B2B2B;
                border: 1px solid #3D3D3D;
                border-radius: 6px;
                padding: 4px;
            }
        """)

    def add_vlan(self, vlan_id, vlan_name, color):
        if vlan_id in self.existing_vlans:
            return  # Skip duplicate VLAN

        vlan_widget = QtWidgets.QWidget()
        vlan_layout = QtWidgets.QHBoxLayout(vlan_widget)
        vlan_layout.setContentsMargins(2, 2, 2, 2)
        vlan_layout.setSpacing(4)
        vlan_widget.setLayout(vlan_layout)

        color_label = QtWidgets.QLabel("   ")
        color_label.setFixedSize(20, 20)
        color_label.setStyleSheet(f"background-color: {color}; border: 1px solid #FFFFFF;")
        vlan_layout.addWidget(color_label)

        text_label = QtWidgets.QLabel(f" VLAN {vlan_id}: {vlan_name}")
        vlan_layout.addWidget(text_label)

        # Add to grid layout with 4 columns
        self.grid_layout.addWidget(vlan_widget, self.current_row, self.current_col)
        self.current_col += 1
        if self.current_col >= 4:
            self.current_col = 0
            self.current_row += 1

        self.existing_vlans.add(vlan_id)  # Add VLAN ID to existing

    def clear_legends(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.existing_vlans.clear()  # Clear existing VLAN IDs
        self.current_row = 0
        self.current_col = 0
