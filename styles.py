BASE_STYLE = """
QToolTip {
    background-color: #2B2B2B;
    color: #FFFFFF;
    border: 1px solid #4CAF50;
    border-radius: 4px;
    padding: 8px;
    font-size: 14px;
    font-weight: bold;
    opacity: 255;
}

* {
    background-color: #2B2B2B;
    color: #E0E0E0;
}

QMainWindow, QWidget {
    background: #2B2B2B;
    color: #E0E0E0;
    background-color: #2B2B2B;
}

QLabel {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 500;
    border-radius: 4px;
    padding: 4px;
}

QLabel[heading="true"] {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: bold;
    margin: 15px;
    letter-spacing: 0.5px;
    border-radius: 6px;
    padding: 5px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

QWidget {
    border: none;
    outline: none;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QRadioButton {
    font-size: 14px;
    color: #FFFFFF;
    padding: 5px;
    spacing: 8px;
}

QPushButton {
    background-color: #3D3D3D;
    border: 2px solid #3D3D3D;
    border-radius: 4px;
    color: #FFFFFF;
    font-size: 14px;
    padding: 8px 16px;
    min-height: 20px;
    transition: all 0.2s ease-in-out;
}

QPushButton:hover {
    background-color: #4D4D4D;
    border: 2px solid #4CAF50;
}

QPushButton:pressed {
    background-color: #4CAF50;
}

QPushButton:checked {
    background-color: #4D4D4D;
    border: 3px solid #4CAF50;
}

QComboBox {
    background-color: #3D3D3D;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    padding: 5px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #4CAF50;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}
"""

GROUPBOX_STYLE = """
QGroupBox {
    border: 1px solid #3D3D3D;
    background-color: #2B2B2B;
    border-radius: 6px;
    margin-top: 10px;
    padding: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    margin-left: 15px;
    background-color: #2B2B2B;
    border-radius: 3px;
    font-size: 14px;
    font-weight: bold;
    color: #FFFFFF;
}

QLineEdit {
    background-color: #3D3D3D;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    padding: 5px;
    color: #FFFFFF;
}

QLineEdit:focus {
    border-color: #4CAF50;
}

QPlainTextEdit {
    background-color: #2B2B2B;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    color: #FFFFFF;
}
"""

LABEL_STYLE = "QLabel { font-size: 16px; color: #FFFFFF; }"

BASE_STYLE += """
QScrollBar:vertical {
    border: none;
    background: #2B2B2B;
    width: 14px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #3D3D3D;
    min-height: 30px;
    border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
    background: #4D4D4D;
}

QScrollBar::add-line:vertical {
    height: 0px;
}

QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #2B2B2B;
    height: 14px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:horizontal {
    background: #3D3D3D;
    min-width: 30px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal:hover {
    background: #4D4D4D;
}

QScrollBar::add-line:horizontal {
    width: 0px;
}

QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QScrollArea {
    border: none;
    background: transparent;
}
"""