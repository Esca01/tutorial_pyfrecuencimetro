#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 11:40:26 2019

@author: EDUCARTE
"""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic # llama al archivo disenofinal.ui

import time
import publicador # publicador.py --> PublicaNota() --> numeroMIDI, frecHz, notaProxima, distNotaProxima

class Proceso(QObject):   # frec 7Hz
    def __init__(self):
        super(Proceso, self).__init__()
        
    def procesoPub(self):
        publicador.PublicaNota()
        
class Ventana(QMainWindow):  # 60Hz --> 100Hz
    def __init__(self):
        super(Ventana, self).__init__()
        uic.loadUi("disenofinal.ui", self)  #P1: mostraba la GUI  disenofinal.ui
        
        #Usamos multihilos Qt
        self.hilo = QThread()
        self.proceso = Proceso()
        self.proceso.moveToThread(self.hilo)
        
        self.boton.clicked.connect(self.hilo.start)
        self.hilo.started.connect(self.proceso.procesoPub)  #P2: Comienza el programa principal "publicador.py"

        self.timer = QTimer()
        self.timer.setInterval(10) # cada 10ms se actualiza la ventana (100Hz)
        self.timer.timeout.connect(self.actualizaVentana)
        self.timer.start()
        
    def actualizaVentana(self): #Recibe los datos: numeroMIDI, frecHz, notaProxima, distNotaProxima
       #el numero MIDI varia de 39 a 65 
        pub_numeroMIDI =  "%.2f" % (publicador.numeroMIDI) #tomamos solo 2 decimales
        self.ResMidi.setText(str(pub_numeroMIDI)) #actualizamos etiqueta MIDI
        
        pub_frecHz =  "%.2f" % (publicador.frecHz)
        self.ResFrec.setText(str(pub_frecHz)) #actualizamos etiqueta frec Hz
        
        self.ResNota.setText(str(publicador.notaProxima))  #actualizamos etiqueta Nota Prox                   
                            
        distNP = "%.2f" % (publicador.distNotaProxima)
        self.ResDist.setText(str(distNP)) #actualizamos etiqueta distancia a la nota prox
        
        self.verticalSlider.setValue((publicador.numeroMIDI)*10) #actualizamos slider
        
        
#P1: mostraba la GUI  disenofinal.ui
def run():
    app = QApplication(sys.argv)
    programa = Ventana()
    programa.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run()
