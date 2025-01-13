BASE_STYLE = """
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
