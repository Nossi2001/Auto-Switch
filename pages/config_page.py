# pages/config_page.py

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QClipboard
from config import Cisco_Router, Cisco_Switch, description_color, methods_inputs, optional_params
from template_logic import TEMPLATE_FUNCTIONS, TemplateError, assign_interface_labels
import os

def adjust_color(hex_color, factor=0.1):
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2],16) for i in (0,2,4)]
    luminance = 0.299*r+0.587*g+0.114*b
    if luminance>76.5:
        r=max(int(r*(1-factor)),0)
        g=max(int(g*(1-factor)),0)
        b=max(int(b*(1-factor)),0)
    else:
        r=min(int(r+(255-r)*factor),255)
        g=min(int(g+(255-g)*factor),255)
        b=min(int(b+(255-b)*factor),255)
    return f"#{r:02X}{g:02X}{b:02X}"

class PortButton(QtWidgets.QPushButton):
    def __init__(self,label=''):
        super().__init__(label)
        self.setCheckable(True)
        self.current_color='#5F5F5F'
        self.hover_color=adjust_color(self.current_color,0.1)
        self.checked_color=adjust_color(self.current_color,0.2)
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color:{self.current_color};
                border:2px solid #9E9E9E;
                border-radius:5px;
                color:#FFFFFF;
            }}
            QPushButton:hover {{
                background-color:{self.hover_color};
                border-color:#4CAF50;
            }}
            QPushButton:checked {{
                background-color:{self.checked_color};
                border-color:#388E3C;
            }}
        """)

    def set_color(self,color):
        self.current_color=color
        self.hover_color=adjust_color(color,0.1)
        self.checked_color=adjust_color(color,0.2)
        self.update_style()

class VLANLegend(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout=QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("""
            QLabel {
                font-size:14px;
                color:#FFFFFF;
            }
            QWidget {
                background-color:#3C3C3C;
                border:1px solid #9E9E9E;
                border-radius:5px;
            }
        """)

    def add_vlan(self,vlan_id,vlan_name,color):
        vlan_widget=QtWidgets.QWidget()
        vlan_layout=QtWidgets.QHBoxLayout()
        vlan_widget.setLayout(vlan_layout)
        color_label=QtWidgets.QLabel("   ")
        color_label.setFixedSize(20,20)
        color_label.setStyleSheet(f"background-color:{color};border:1px solid #FFFFFF;")
        vlan_layout.addWidget(color_label)
        text_label=QtWidgets.QLabel(f" VLAN {vlan_id}: {vlan_name}")
        vlan_layout.addWidget(text_label)
        self.layout.addWidget(vlan_widget)

    def clear_legends(self):
        while self.layout.count():
            child=self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

class ConfigPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget=stacked_widget
        self.device_type=None
        self.device_name=None
        self.methods=[]
        self.physical_interfaces=[]
        self.port_buttons={}
        self.used_vlans={}
        self.labeled_interfaces=[]
        self.full_config = ""  # Zmienna przechowująca zsumowaną konfigurację

        self.setStyleSheet("""
            QWidget {
                background-color:#2B2B2B;
                color:#FFFFFF;
                font-family:Arial;
            }
            QGroupBox {
                border:1px solid #9E9E9E;
                margin-top:10px;
            }
            QGroupBox::title {
                subcontrol-origin:margin;
                subcontrol-position:top center;
                padding:0 3px;
                color:#FFFFFF;
            }
            QLabel {
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
        """)

        self.main_layout=QtWidgets.QVBoxLayout()
        placeholder_label=QtWidgets.QLabel("Proszę wybrać urządzenie na poprzedniej stronie...")
        placeholder_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(placeholder_label)
        self.setLayout(self.main_layout)

        self.params_group=None
        self.params_layout=None
        self.param_widgets={}
        self.vlan_legend=None

    def initialize(self,device_type,device_name):
        self.device_type=device_type
        self.device_name=device_name
        self.used_vlans={}
        self.full_config = ""  # reset konfiguracji przy przejściu do nowego urządzenia

        if self.device_type=='router':
            if device_name not in Cisco_Router:
                QtWidgets.QMessageBox.critical(self,"Error",f"Router '{device_name}' nie znaleziony.")
                return
            device_data=Cisco_Router[device_name]
            device_label="Router"
        else:
            if device_name not in Cisco_Switch:
                QtWidgets.QMessageBox.critical(self,"Error",f"Switch '{device_name}' nie znaleziony.")
                return
            device_data=Cisco_Switch[device_name]
            device_label="Switch"

        self.methods=device_data.get('method_list',[])
        self.physical_interfaces=device_data.get('interfaces',[])
        self.labeled_interfaces=assign_interface_labels(self.physical_interfaces)

        self.setup_ui_elements(device_label)

    def clear_layout(self,layout):
        if layout is not None:
            while layout.count():
                item=layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def setup_ui_elements(self,device_label):
        self.clear_layout(self.main_layout)
        header_label=QtWidgets.QLabel(f"Urządzenie: {self.device_name} ({device_label})")
        header_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size:20px;font-weight:bold;")
        self.main_layout.addWidget(header_label)

        ports_group=QtWidgets.QGroupBox("Porty")
        ports_layout=QtWidgets.QVBoxLayout()
        ports_group.setLayout(ports_layout)
        ports_container=QtWidgets.QWidget()

        grid_layout=QtWidgets.QGridLayout()
        grid_layout.setSpacing(5)
        columns=14
        row=0
        col=0

        self.port_buttons={}
        for iface in self.labeled_interfaces:
            # Skrócona nazwa już jest (Fa, Gi), iface['label'] to np. Fa0/0
            # Wyświetlamy "Fa0/0"
            port_label=f"{iface['label']}"
            btn=PortButton(port_label)
            btn.setProperty("interface_name",iface['name'])
            self.port_buttons[port_label]=btn

            grid_layout.addWidget(btn,row,col)
            col+=1
            if col>=columns:
                col=0
                row+=1

        ports_container.setLayout(grid_layout)
        ports_layout.addWidget(ports_container)
        self.main_layout.addWidget(ports_group)

        methods_group=QtWidgets.QGroupBox("Metody")
        methods_layout=QtWidgets.QVBoxLayout()
        methods_group.setLayout(methods_layout)

        self.method_combo=QtWidgets.QComboBox()
        self.method_combo.addItems(self.methods)
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        methods_layout.addWidget(self.method_combo)
        methods_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.params_group=QtWidgets.QGroupBox("Parametry Metody")
        self.params_layout=QtWidgets.QFormLayout()
        self.params_group.setLayout(self.params_layout)
        methods_layout.addWidget(self.params_group)
        self.main_layout.addWidget(methods_group)

        apply_button=QtWidgets.QPushButton("Zastosuj Konfigurację")
        apply_button.clicked.connect(self.apply_configuration)
        self.main_layout.addWidget(apply_button)

        # Przyciski: Wróć, Skopiuj, Zapisz do pliku
        bottom_layout = QtWidgets.QHBoxLayout()

        back_button = QtWidgets.QPushButton("Wróć")
        back_button.clicked.connect(self.go_back)
        bottom_layout.addWidget(back_button)

        copy_button = QtWidgets.QPushButton("Skopiuj całą konfigurację")
        copy_button.clicked.connect(self.copy_entire_config)
        bottom_layout.addWidget(copy_button)

        save_button = QtWidgets.QPushButton("Prześlij do pliku")
        save_button.clicked.connect(self.save_entire_config)
        bottom_layout.addWidget(save_button)

        self.main_layout.addLayout(bottom_layout)

        self.vlan_legend=VLANLegend()
        self.main_layout.addWidget(self.vlan_legend)

        self.on_method_changed(self.method_combo.currentIndex())

    def go_back(self):
        # Powrót do strony startowej
        self.stacked_widget.setCurrentIndex(0)

    def copy_entire_config(self):
        cb = QtWidgets.QApplication.clipboard()
        cb.setText(self.full_config, mode=QClipboard.Mode.Clipboard)
        QtWidgets.QMessageBox.information(self,"Skopiowano","Cała konfiguracja została skopiowana do schowka.")

    def save_entire_config(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Zapisz konfigurację","","Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename,"w") as f:
                    f.write(self.full_config)
                QtWidgets.QMessageBox.information(self,"Zapisano","Konfiguracja zapisana do pliku.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self,"Błąd zapisu",f"Nie udało się zapisać pliku: {e}")

    def on_method_changed(self,index):
        self.clear_layout(self.params_layout)
        self.param_widgets={}
        method_name=self.method_combo.currentText()
        input_params=methods_inputs.get(method_name,[])
        opt=optional_params.get(method_name,[])

        for p in input_params:
            label_text=p
            if p in opt:
                label_text+=" (!)"
            widget=self.create_input_widget(p)
            self.params_layout.addRow(label_text+":",widget)
            self.param_widgets[p]=widget

        self.update_dynamic_fields()

    def create_input_widget(self,param_name):
        lower=param_name.lower()
        if "interface" in lower:
            label=QtWidgets.QLabel("Wybrane z zaznaczonych portów")
            return label
        if "routing protocol" in lower:
            combo=QtWidgets.QComboBox()
            combo.addItems(["OSPF","EIGRP"])
            return combo
        if "vlan routing" in lower or "dhcp server" in lower:
            chk=QtWidgets.QCheckBox()
            return chk
        if "color" in lower:
            btn=QtWidgets.QPushButton("Wybierz Kolor")
            btn.clicked.connect(lambda _,b=btn:self.select_color(b))
            return btn
        if "vlan id" in lower or "process id" in lower or "area id" in lower:
            spin=QtWidgets.QSpinBox()
            spin.setRange(1,65535)
            return spin
        line=QtWidgets.QLineEdit()
        return line

    def select_color(self,button):
        color=QtWidgets.QColorDialog.getColor()
        if color.isValid():
            hex_color=color.name()
            button.setStyleSheet(f"background-color:{hex_color};")
            button.setProperty("selected_color",hex_color)

    def update_dynamic_fields(self):
        pass

    def apply_configuration(self):
        selected_method=self.method_combo.currentText()
        selected_ports=[btn.property("interface_name") for btn in self.port_buttons.values() if btn.isChecked()]

        input_params=methods_inputs.get(selected_method,[])
        interface_params=[p for p in input_params if "interface" in p.lower()]
        required_interfaces=len(interface_params)

        if interface_params:
            if len(selected_ports)<required_interfaces:
                QtWidgets.QMessageBox.warning(self,"Błąd",f"Metoda '{selected_method}' wymaga wybrania {required_interfaces} portów.")
                return

        params_values={}
        opt=optional_params.get(selected_method,[])
        iface_count=0
        for label,widget in self.param_widgets.items():
            if "interface" in label.lower():
                port=selected_ports[iface_count]
                iface_count+=1
                params_values[label]=port
            elif isinstance(widget,QtWidgets.QSpinBox):
                params_values[label]=widget.value()
            elif isinstance(widget,QtWidgets.QCheckBox):
                params_values[label]=widget.isChecked()
            elif isinstance(widget,QtWidgets.QComboBox):
                params_values[label]=widget.currentText()
            elif isinstance(widget,QtWidgets.QPushButton) and "color" in label.lower():
                params_values[label]=widget.property("selected_color") or ""
            elif isinstance(widget,QtWidgets.QLineEdit):
                params_values[label]=widget.text().strip()

        used_vlans_ids=set(self.used_vlans.keys())
        used_vlans_names=set(v['name'] for v in self.used_vlans.values())

        func=TEMPLATE_FUNCTIONS.get(selected_method,None)
        if not func:
            QtWidgets.QMessageBox.warning(self,"Błąd",f"Brak logiki dla metody: {selected_method}")
            return

        try:
            if selected_method=="apply_data_template":
                config_text=func(params_values,selected_ports,used_vlans_ids,used_vlans_names)
            else:
                config_text=func(params_values,selected_ports)

            # Dodajemy wygenerowaną konfigurację do self.full_config
            if config_text.strip():
                if self.full_config.strip():
                    self.full_config += "\n! --- Kolejna konfiguracja ---\n"
                self.full_config += config_text+"\n"

            QtWidgets.QMessageBox.information(self,"Wygenerowana Konfiguracja",config_text)

            if selected_method in ["apply_data_template","apply_static_routing","apply_dynamic_routing","apply_nat","apply_dhcp_server","default_interface"]:
                if selected_method=="apply_data_template":
                    vlan_id=params_values.get("VLAN ID","")
                    vlan_name=params_values.get("Profile Name","")
                    color=params_values.get("Color","")
                    self.used_vlans[vlan_id]={'name':vlan_name,'color':color}
                    self.vlan_legend.add_vlan(vlan_id,vlan_name,color)

        except TemplateError as e:
            QtWidgets.QMessageBox.warning(self,"Błąd Walidacji",str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,"Błąd",f"Nieoczekiwany błąd: {e}")
