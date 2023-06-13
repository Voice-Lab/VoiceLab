#!/usr/bin/env python

import sys
import os
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(THIS_DIR)
print(PARENT_DIR)
VOICELAB_DIR = os.path.join(PARENT_DIR, '/voicelab/src')
sys.path.insert(0, ''.join([VOICELAB_DIR, "/Voicelab/toolkits/Voicelab"]))

sys.path.insert(0, PARENT_DIR)
sys.path.insert(0, VOICELAB_DIR)
import qdarkstyle
import sys


#from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#from voicelab.src.Voicelab.VoicelabGUI.InputTab import InputTab
#from voicelab.src.Voicelab.VoicelabGUI.OutputTab import OutputTab
#from voicelab.src.Voicelab.VoicelabGUI.SettingsTab import SettingsTab
#from voicelab.src.Voicelab.VoicelabGUI.VoicelabController import VoicelabController
#from voicelab.src.Voicelab.default_settings import available_functions, default_functions

from __main__ import VoicelabWizard

def main():
    # boilerplate pyqt window creation
    app = QApplication(sys.argv)
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Create an instance of VoiceLab
    w = VoicelabWizard()
    # Show the GUI
    w.show()
    # Exit gracefully
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()