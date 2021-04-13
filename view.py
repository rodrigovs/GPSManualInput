# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:34:08 2021

@author: Rodrigo
"""
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QGraphicsPixmapItem, QWidget, QTableWidgetItem)

from PyQt5.QtGui import QPixmap, QImage, QBrush, QColor
import sys
import glob
import serial
import time
from io import BytesIO
from PIL import Image
import requests

import threading

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        
        self.contador_coordenada = 0
        self.plain_text_coordenadas_enviadas = ''
        self.filename_coordenadas = 'viagem_vinicius_2901.txt'
        self.serial_port = 'COM3'
        self.serial_baudrate = 115200
        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        # self.createBottomLeftTabWidget()
        # self.createBottomRightGroupBox()
        # self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)
        
        
        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        # mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        # mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        # mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        
        
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("GPS tool ESP32")
        self.resize(800,500)
        self.changeStyle('Fusion')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def createTopLeftGroupBox(self):
        
        self.topLeftGroupBox = QTabWidget()
        self.topLeftGroupBox.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        
        
        
        lines = tuple(open(self.filename_coordenadas, 'r'))
        tableWidget = QTableWidget(len(lines), 1)
        linhas_filtradas = []

        for num,line in enumerate(lines, start=0):
            
            if(('*') in line):
                break
            
            linhas_filtradas.append(line)
            print(str(num) + ' : ' + line)
            tItem = QTableWidgetItem()
            tItem.setText(line)
            tableWidget.setItem(num,0,tItem)
        
        self.lista_coordenadas = linhas_filtradas
        # qb = QBrush()
        # qb.setColor(QColor.blue)
        # tItem3.setBackground(QtGui.color.blue)
        
        
        # tableWidget.setItem(1,0,tItem2)
        # tableWidget.setItem(2,0,tItem3)
        tableWidget.setColumnWidth(0,320)
        
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(0, 0,0, 0)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        self.textEdit = QTextEdit()

        self.textEdit.setPlainText("nada ainda")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.textEdit)
        tab2.setLayout(tab2hbox)
        
        self.topLeftGroupBox.addTab(tab1, "Coordenadas &Inseridas")
        self.topLeftGroupBox.addTab(tab2, "Coordenadas &Enviadas")

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Mapa")

        defaultPushButton = QPushButton("Enviar coordenada")
        defaultPushButton.setDefault(True)
        defaultPushButton.clicked.connect(lambda:self.btn_enviar_coordenada_pressed())
        
        
        connectCOMPushButton = QPushButton("Conectar COM")
        connectCOMPushButton.clicked.connect(lambda:self.btn_conectar_serial())
        
        unconnectCOMPushButton = QPushButton("Desconectar COM")
        unconnectCOMPushButton.clicked.connect(lambda:self.btn_desconectar_serial())
        
        setGPSManualModePushButton = QPushButton("Set GPS Manual Mode")
        setGPSManualModePushButton.clicked.connect(lambda:self.btn_set_gps_manual_mode())
        
        poiHandlePushButton = QPushButton("Enviar POI HANDLE")
        poiHandlePushButton.clicked.connect(lambda:self.btn_enviar_poi_handle())
        
        self.autoModePushButton = QPushButton("Modo automático")
        self.autoModePushButton.setCheckable(False)
        self.autoModePushButton.setStyleSheet("background-color : red")
        
        # self.autoModePushButton.toogl.connect()
        # self.autoModePushButton.isDown.connect(lambda:self.btn_play_auto_coordinates_mode(4))
        self.autoModePushButton.clicked.connect(lambda:self.btn_change_play_auto_state())
        url = "https://maps.googleapis.com/maps/api/staticmap?center=-25.429749,-49.240508&markers=color:blue%7Clabel:P%7C-25.429749,-49.240508&zoom=17&size=400x400&maptype=roadmap&key=AIzaSyAn540o6KOJ117r0h5USUIUz3mWNp0fl7E"
        request = requests.get(url)
       # buffer = BytesIO(request.content)

        pixmap = QPixmap()
        pixmap.loadFromData(request.content)
        
        self.labelMapa = QLabel(self)
        self.labelMapa.setPixmap(pixmap)

        layout = QVBoxLayout()
        layout.addWidget(self.labelMapa)
        layout.addWidget(defaultPushButton)
        layout.addWidget(poiHandlePushButton)
        layout.addWidget(self.autoModePushButton)
        layout.addWidget(setGPSManualModePushButton)
        layout.addWidget(connectCOMPushButton)
        layout.addWidget(unconnectCOMPushButton)
        
        
        layout.addStretch(1)
        
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QGroupBox("Coordenadas")

        radioButton1 = QRadioButton("Radio button 1")
        radioButton2 = QRadioButton("Radio button 2")
        radioButton3 = QRadioButton("Radio button 3")
        radioButton1.setChecked(True)

        checkBox = QCheckBox("Tri-state check box")
        checkBox.setTristate(True)
        checkBox.setCheckState(Qt.PartiallyChecked)

        layout = QVBoxLayout()
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addWidget(checkBox)
        layout.addStretch(1)
        self.bottomLeftTabWidget.setLayout(layout)    

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Group 3")
        self.bottomRightGroupBox.setCheckable(True)
        self.bottomRightGroupBox.setChecked(True)

        lineEdit = QLineEdit('s3cRe7')
        lineEdit.setEchoMode(QLineEdit.Password)

        spinBox = QSpinBox(self.bottomRightGroupBox)
        spinBox.setValue(50)

        dateTimeEdit = QDateTimeEdit(self.bottomRightGroupBox)
        dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
        slider.setValue(40)

        scrollBar = QScrollBar(Qt.Horizontal, self.bottomRightGroupBox)
        scrollBar.setValue(60)

        dial = QDial(self.bottomRightGroupBox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(lineEdit, 0, 0, 1, 2)
        layout.addWidget(spinBox, 1, 0, 1, 2)
        layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scrollBar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)
        
    def btn_enviar_coordenada_pressed(self):
        
        if( self.contador_coordenada + 1 <= len(self.lista_coordenadas)):
            
            string_coordenada = self.lista_coordenadas[self.contador_coordenada].split('\n')[0]
           
            self.plain_text_coordenadas_enviadas += str(self.contador_coordenada) + " - " + string_coordenada + "\n"
            
            print('coordenada enviada: '+ str(self.contador_coordenada) + " - " + string_coordenada)
            
            self.textEdit.setPlainText(self.plain_text_coordenadas_enviadas)
            self.contador_coordenada += 1
            
            
            string_lat_lon = string_coordenada.split('_')[0] + "," + string_coordenada.split('_')[1]
            url = "https://maps.googleapis.com/maps/api/staticmap?center=" + string_lat_lon +"&markers=color:blue%7Clabel:P%7C" + string_lat_lon + "&zoom=17&size=400x400&maptype=roadmap&key=AIzaSyAn540o6KOJ117r0h5USUIUz3mWNp0fl7E"

            request = requests.get(url)
           # # buffer = BytesIO(request.content)
    
            pixmap = QPixmap()
            pixmap.loadFromData(request.content)
            self.labelMapa.setPixmap(pixmap)
           #  label = QLabel(self)
           #  label.setPixmap(pixmap)



            
            self.serial_connection.write(b'GPS\n')
            print('enviando: ' + string_coordenada)
            self.serial_connection.write(bytes(string_coordenada,'ascii'))
            # time.sleep(5)
            # print('enviando POI_HANDLE')
            # self.serial_connection.write(b'POI_HANDLE')

            
        else:
            self.plain_text_coordenadas_enviadas += "Fim das coordenadas" + " \n"
            self.textEdit.setPlainText(self.plain_text_coordenadas_enviadas)
            return(0)
        
        return(1)
    
    def btn_enviar_poi_handle(self):
        print('enviando POI_HANDLE')
        self.serial_connection.write(b'POI_HANDLE')
    
    def btn_conectar_serial(self):
        print('Conectar Serial')
        lista_available_coms = self.serial_ports()
        if(not(self.serial_port in lista_available_coms)):
            print(self.serial_port + ' nao exibida na lista, tente outro nome')
            print(lista_available_coms)
            sys.exit()



        self.serial_connection = serial.Serial(port=self.serial_port, baudrate=self.serial_baudrate)

        thread_input_data = threading.Thread(target=self.read_serial)
        thread_input_data.start()
        
        
    def btn_desconectar_serial(self):
        print('desconectar Serial')
        self.serial_connection.close()
        print("Conexao encerrada")
        

    def read_serial(self):
        while True:
            #print(serial_connection.readline())
            print(self.serial_connection.readline())
            
            # if(clear_output):
            #     output = ''
            # output += serial_connection.read_all()
            # #linhas = output.split('\n')
            # clear_output = True
            # if(len(output) > 0):
            #     print(output)
                        

        
    
    def btn_set_gps_manual_mode(self):
        print('Modo manual setado')
        print('enviando set manual mode')
        self.serial_connection.write(b'SET_GPS_MANUAL_MODE\n')
        
        
        
        
        
    def btn_change_play_auto_state(self):
        
        
        if(self.autoModePushButton.isChecked()):
            print('false')
            self.autoModePushButton.setCheckable(False) 
            self.autoModePushButton.setStyleSheet("background-color : red") 
                       
            
        else:
            print('true')
            self.autoModePushButton.setCheckable(True)  
            self.autoModePushButton.setStyleSheet("background-color : green")
            
        
        
        
    def btn_play_auto_coordinates_mode(self,stime):
        print('Modo automático acionado com tempo: ' + str(stime))
        print('play_auto')
        self.btn_enviar_coordenada_pressed()
        time.sleep(stime)
        self.btn_enviar_poi_handle()
        time.sleep(stime)
        # res = 1
        # while(res != 0):
        #     print('auto mode ligado')
        #     res = 
        
        
        
        
        
        
    def serial_ports(self):
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
            """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result



app = QApplication(sys.argv)
gallery = WidgetGallery()
gallery.show()
sys.exit(app.exec_())
