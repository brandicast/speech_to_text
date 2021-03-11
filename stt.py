import time
import speech_recognition as sr
import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
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
    global language
    try:
        updater.updateStatus.emit ('開始辨識')
        print ('language = {0}', language )
        recog = recognizer.recognize_google(audio, language=language)
        updater.updateStatus.emit ('辨識結束')
        recognized_text =  recognized_text + recog + '\n'
        updater.updateText.emit(recognized_text)
        print("Google Speech Recognition thinks you said " + recog )
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        updater.showMessage.emit ('網路好像有問題 !')

def withMicrophone():
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

def withAudioFile():
    global audioFilename

    if audioFilename:
        w.pushButton.setEnabled (False)
        w.compareButton.setEnabled (False)

        t = threading.Thread (target = processAudioFile, args=(audioFilename,) )
        t.start()
        #processAudioFile (audioFilename)


        audioFilename = ''
    else:
        QMessageBox.information(None, 'Warning','Please selec a valid audio file',QMessageBox.Close)
        
def processAudioFile (filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source: 
        audio = r.record (source)
        callback(r,audio)
    w.pushButton.setEnabled (True)
    w.compareButton.setEnabled (True)
        


def go():
    if input_source_is_mic :
        withMicrophone()
    else:
        withAudioFile()

        
def compare():
    #go()
    a = w.plainTextEdit.toPlainText()
    b = w.plainTextEdit_2.toPlainText()
    print(sim.similarity(a,b))
    print (sim.likelihood(a, b))
    if a and b:
        #w.lcdNumber.display(round(sim.similarity(a,b),2))
        w.lcdNumber.display(round(sim.similarity(a,b),2))
        w.lcdNumber_2.display(round(sim.likelihood(a, b),2))
    


class Updater(QObject):                                                                                           
    updateText = pyqtSignal(str)   
    updateStatus = pyqtSignal(str)  
    showMessage = pyqtSignal(str)


def showMessage(text):
    msg.label_2.setText(text)
    ui_msg.show()

def setLanguage ():
    global language
    
    if w.sender().objectName() == 'actionEnglish':
        language = 'en-US'
        w.actionMandarin.setChecked(False)
        w.actionEnglish.setChecked(True)
    else :
        language = 'zh-TW'
        w.actionMandarin.setChecked(True)
        w.actionEnglish.setChecked(False)
    w.menuLanguage.show()

def setInputSource ():
    global input_source_is_mic
    
    if w.sender().objectName() == 'actionMicrophone':
        input_source_is_mic = True
        w.actionMicrophone.setChecked (True)
        w.statusbar.showMessage('Input Source is Microphone')
    else:
        input_source_is_mic = False
        w.actionMicrophone.setChecked (False)
    w.menuInput_Source.show()
    

def selectFile ():
    global audioFilename
    input_source_is_mic = False
    #fileName,_ = QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","Audio File(*.m4a)")
    fileName,_ = QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","Audio File(*.*)")
    w.statusbar.showMessage('Input Source is File: ' + fileName)
    audioFilename = fileName



isStart = True 
recognized_text = ''
#language = 'zh-TW'
language = 'en-US'
input_source_is_mic = True
audioFilename = ''
updater = Updater()

app = QApplication(sys.argv)

w = loadUi('main.ui')
about = loadUi('about.ui')
msg = loadUi('msg.ui')

w.progressBar.setVisible (False)


w.actionExit.triggered.connect(app.exit)
w.actionEnglish.triggered.connect(setLanguage)
w.actionMandarin.triggered.connect(setLanguage)

w.actionMicrophone.triggered.connect(setInputSource)
w.menuAudio_File.triggered.connect(setInputSource)
w.actionOpen.triggered.connect (selectFile)


updater.updateText.connect(w.plainTextEdit.setPlainText, Qt.QueuedConnection)
updater.updateStatus.connect(w.statusbar.showMessage, Qt.QueuedConnection )

w.actionAbout.triggered.connect (about.show)
about.pushButton.clicked.connect(about.hide)
msg.pushButton.clicked.connect(msg.hide)

updater.showMessage.connect(showMessage, Qt.QueuedConnection )

w.pushButton.clicked.connect(go)
w.compareButton.clicked.connect(compare)

w.show()

app.exec_()