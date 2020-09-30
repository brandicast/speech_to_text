import time
import speech_recognition as sr
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore  import QObject, pyqtSignal, Qt
from PyQt5 import QtWidgets
import similarity as sim

from main import Ui_MainWindow 
from about import Ui_Dialog as Ui_Dialog_about
from msg import Ui_Dialog as Ui_Dialog_msg




# this is called from the background threa]d
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    global recognized_text
    try:
        updater.updateStatus.emit ('開始辨識')
        recog = recognizer.recognize_google(audio, language='zh-tw')
        updater.updateStatus.emit ('辨識結束')
        recognized_text =  recognized_text + recog + '\n'
        updater.updateText.emit(recognized_text)
        print("Google Speech Recognition thinks you said " + recog )
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        updater.showMessage.emit ('網路好像有問題 !')

def go():
    global isStart
    global stop_listening
    global recognized_text
    if isStart :
        try:
            
            
            r = sr.Recognizer()
            with sr.Microphone() as m:
                r.adjust_for_ambient_noise(m)   
            stop_listening = r.listen_in_background(m, callback)
            print (f'{r.energy_threshold} : {r.dynamic_energy_threshold} : {r.pause_threshold} : {r.operation_timeout}')
            recognized_text = ''
            updater.updateText.emit('')
            w.pushButton.setText('停止')
            isStart = False
            updater.updateStatus.emit ('') 
            w.lcdNumber.display (0)
            w.lcdNumber_2.display (0)
            w.compareButton.setEnabled (False)
        except OSError as err:
            print (err)
            msg.label_2.setText('請確認麥克風是否開啟')
            ui_msg.show()
    else :
        w.pushButton.setText('開始')
        updater.updateStatus.emit ('') 
        stop_listening()
        isStart = True
        w.compareButton.setEnabled (True)
        
def compare():
    #go()
    a = w.plainTextEdit.toPlainText()
    b = w.plainTextEdit_2.toPlainText()
    print(sim.similarity(a,b))
    print (sim.likelihood(a, b))
    if a and b:
        w.lcdNumber.display(round(sim.similarity(a,b),2))
        w.lcdNumber_2.display(round(sim.likelihood(a, b),2))
    


class Updater(QObject):                                                                                           
    updateText = pyqtSignal(str)   
    updateStatus = pyqtSignal(str)  
    showMessage = pyqtSignal(str)


def showMessage(text):
    msg.label_2.setText(text)
    ui_msg.show()

updater = Updater()


isStart = True 
recognized_text = ''

app = QApplication(sys.argv)

'''
w = loadUi('main.ui')
about = loadUi('about.ui')
msg = loadUi('msg.ui')
'''



ui_w = QtWidgets.QMainWindow()
w = Ui_MainWindow()
w.setupUi(ui_w)

ui_about = QtWidgets.QDialog()
about = Ui_Dialog_about()
about.setupUi(ui_about)

ui_msg = QtWidgets.QDialog()
msg = Ui_Dialog_msg()
msg.setupUi(ui_msg)


w.pushButton.clicked.connect(go)

updater.updateText.connect(w.plainTextEdit.setPlainText, Qt.QueuedConnection)
updater.updateStatus.connect(w.statusbar.showMessage, Qt.QueuedConnection )
w.actionAbout.triggered.connect (ui_about.show)
about.pushButton.clicked.connect(ui_about.hide)
msg.pushButton.clicked.connect(ui_msg.hide)
updater.showMessage.connect(showMessage, Qt.QueuedConnection )
w.compareButton.clicked.connect(compare)
w.actionExit.triggered.connect(app.exit)

ui_w.show()
app.exec_()