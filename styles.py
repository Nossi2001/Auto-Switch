BASE_STYLE = """
QWidget {
    background-color: #2B2B2B;
    color: #FFFFFF;
    font-family: Arial;
}
QRadioButton {
    font-size:16px;
    color:#FFFFFF;
}
QPushButton {
    background-color:#5F5F5F;
    border:2px solid #9E9E9E;
    border-radius:5px;
    color:#FFFFFF;
    font-size:16px;
    padding:5px 10px;
}
QPushButton:hover {
    border-color:#4CAF50;
    background-color:#6F6F6F;
}
"""

GROUPBOX_STYLE = """
QGroupBox {
    border: 1px solid #9E9E9E;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    color: #FFFFFF;
}
"""

LABEL_STYLE = "QLabel { font-size: 16px; color: #FFFFFF; }"
