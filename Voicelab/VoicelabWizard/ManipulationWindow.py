from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import parselmouth
from parselmouth.praat import call

from Voicelab.default_settings import display_whitelist
from Voicelab.VoicelabWizard.VoicelabTab import VoicelabTab

class ManipulationWindow(VoicelabTab):
    def __init__(self, data_controller, signals, tabs, *args, **kwargs):
        """
        Args:
            data_controller:
            signals:
            tabs:
            *args:
            **kwargs:
        """
        super().__init__(data_controller, signals, tabs, *args, **kwargs)

        self.selected_tab = 0


        grid = QGridLayout()
        grid.addWidget(self.pitchSlider(), 0, 0)
        grid.addWidget(self.formantSlider(), 0, 1)
        grid.addWidget(self.amplitude_Slider(), 1, 0)
        grid.addWidget(self.duration_Slider(), 1, 1)
        self.setLayout(grid)


    def pitchSlider(self):
        groupBox = QGroupBox("Voice Manipulations")

        # title
        self.pitch_slider_title = QLabel()
        self.pitch_slider_title.setText('Pitch')
        self.pitch_slider_title.setAlignment(Qt.AlignTop)


        self.pitch_slider = QSlider(Qt.Horizontal, self)
        self.pitch_slider.setRange(-100, 100)
        #self.pitch_slider.setGeometry(30, 40, 5000, 30)
        self.pitch_slider.setTickPosition(QSlider.TicksBelow)
        self.pitch_slider.valueChanged[int].connect(self.changeValuePitch)

        # label
        self.hbox = QHBoxLayout()
        self.hbox.addStretch()
        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText('-100%')
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText('100%')
        self.hbox.addWidget(label_minimum, Qt.AlignRight)  # , Qt.AlignLeft
        self.hbox.addWidget(self.pitch_slider, Qt.AlignCenter)  # , Qt.AlignCenter
        self.hbox.addWidget(label_maximum, Qt.AlignRight)  # , Qt.AlignRight


        self.vbox = QVBoxLayout()
        #self.vbox.addStretch()
        self.label = QLabel()
        self.vbox.addWidget(self.pitch_slider_title, Qt.AlignLeft)
        self.label.setText('Selected Value: 0')
        self.vbox.addWidget(self.label)
        self.vbox.addLayout(self.hbox)
        groupBox.setLayout(self.vbox)
        return groupBox

    def changeValuePitch(self, value):
        self.pitch_manipulation_amount = value
        size = self.pitch_slider.value()
        self.label.setText(f'Selected Value: {size}')

    def formantSlider(self):
        formant_groupBox = QGroupBox("Voice Manipulations")

        # title
        self.formant_slider_title = QLabel()
        self.formant_slider_title.setText('Formants')
        self.formant_slider_title.setAlignment(Qt.AlignTop)

        # self.formant_checkbox_raised = QCheckBox('Raise')
        # self.formant_checkbox_raised.checkState(True)
        # self.formant_checkbox_lowered = QCheckBox('Lower')
        # self.formant_checkbox_lowered.checkState(True)
        # self.formant_checkbox_raised.stateChanged.connect(lambda: self.formant_checkbox_state(self.ch1, self.ch2))
        # self.formant_checkbox_lowered.stateChanged.connect(lambda: self.formant_checkbox_state(self.ch1, self.ch2))


        self.formant_slider = QSlider(Qt.Horizontal, self)
        self.formant_slider.setRange(0, 100)
        #self.pitch_slider.setGeometry(30, 40, 5000, 30)
        self.formant_slider.setTickPosition(QSlider.TicksBelow)
        self.formant_slider.valueChanged[int].connect(self.changeValueFormants)

        # label
        self.formant_hbox = QHBoxLayout()
        self.formant_hbox.addStretch()

        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText('0% (No change)')
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText('100%')
        self.formant_hbox.addWidget(label_minimum, Qt.AlignRight)  # , Qt.AlignLeft
        self.formant_hbox.addWidget(self.formant_slider, Qt.AlignCenter)  # , Qt.AlignCenter
        self.formant_hbox.addWidget(label_maximum, Qt.AlignRight)  # , Qt.AlignRight

        self.formant_vbox = QVBoxLayout()
        #self.vbox.addStretch()
        self.formant_label = QLabel()
        self.formant_vbox.addWidget(self.formant_slider_title, Qt.AlignLeft)
        self.formant_label.setText('Selected Value: 0')
        self.formant_vbox.addWidget(self.formant_label)
        self.formant_vbox.addLayout(self.formant_hbox)
        formant_groupBox.setLayout(self.formant_vbox)
        return formant_groupBox

    def changeValueFormants(self, value):
        self.formant_manipulation_amount = value
        size = self.formant_slider.value()
        self.formant_label.setText(f'Selected Value: {size}')

    def formant_checkbox_state(self, ch1, ch2):
        if ch1 and not ch2:
            print("Only raise formants")
        if ch2 and not ch1:
            print("Only lower formants")
        if ch2 and ch1:
            print("Raise and lower formants")


    def amplitude_Slider(self):
        amplitude_groupBox = QGroupBox("Voice Manipulations")

        # title
        self.amplitude_slider_title = QLabel()
        self.amplitude_slider_title.setText('Amplitude')
        self.amplitude_slider_title.setAlignment(Qt.AlignTop)

        self.amplitude_slider = QSlider(Qt.Horizontal, self)
        self.amplitude_slider.setRange(0, 100)
        self.amplitude_slider.setValue(80)
        #self.pitch_slider.setGeometry(30, 40, 5000, 30)
        self.amplitude_slider.setTickPosition(QSlider.TicksBelow)
        self.amplitude_slider.valueChanged[int].connect(self.changeValueamplitudes)

        # label
        self.amplitude_hbox = QHBoxLayout()
        self.amplitude_hbox.addStretch()
        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText('0 dB')
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText('100 dB')
        self.amplitude_hbox.addWidget(label_minimum, Qt.AlignRight)  # , Qt.AlignLeft
        self.amplitude_hbox.addWidget(self.amplitude_slider, Qt.AlignCenter)  # , Qt.AlignCenter
        self.amplitude_hbox.addWidget(label_maximum, Qt.AlignRight)  # , Qt.AlignRight

        self.amplitude_vbox = QVBoxLayout()
        #self.vbox.addStretch()
        self.amplitude_label = QLabel()
        self.amplitude_vbox.addWidget(self.amplitude_slider_title, Qt.AlignLeft)
        self.amplitude_label.setText('Selected Value: 80')
        self.amplitude_vbox.addWidget(self.amplitude_label)
        self.amplitude_vbox.addLayout(self.amplitude_hbox)
        amplitude_groupBox.setLayout(self.amplitude_vbox)
        return amplitude_groupBox

    def changeValueamplitudes(self, value):
        self.amplitude_manipulation_amount = value
        size = self.amplitude_slider.value()
        self.amplitude_label.setText(f'Selected Value: {size}')
        
    def duration_Slider(self):
        duration_groupBox = QGroupBox("Voice Manipulations")

        # title
        self.duration_slider_title = QLabel()
        self.duration_slider_title.setText('Duration')
        self.duration_slider_title.setAlignment(Qt.AlignTop)

        self.duration_slider = QSlider(Qt.Horizontal, self)
        self.duration_slider.setRange(50, 200)
        self.duration_slider.setValue(100)

        #self.pitch_slider.setGeometry(30, 40, 5000, 30)
        self.duration_slider.setTickPosition(QSlider.TicksBelow)
        self.duration_slider.valueChanged[int].connect(self.changeValuedurations)

        # label
        self.duration_hbox = QHBoxLayout()
        self.duration_hbox.addStretch()
        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText('0.5x speed')
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText('2x speed')
        self.duration_hbox.addWidget(label_minimum, Qt.AlignRight)  # , Qt.AlignLeft
        self.duration_hbox.addWidget(self.duration_slider, Qt.AlignCenter)  # , Qt.AlignCenter
        self.duration_hbox.addWidget(label_maximum, Qt.AlignRight)  # , Qt.AlignRight

        self.duration_vbox = QVBoxLayout()
        #self.vbox.addStretch()
        self.duration_label = QLabel()
        self.duration_vbox.addWidget(self.duration_slider_title, Qt.AlignLeft)
        self.duration_label.setText('Selected Value: 1')
        self.duration_vbox.addWidget(self.duration_label)
        self.duration_vbox.addLayout(self.duration_hbox)
        duration_groupBox.setLayout(self.duration_vbox)
        return duration_groupBox

    def changeValuedurations(self, value):
        self.duration_manipulation_amount = value
        size = self.duration_slider.value()
        self.duration_label.setText(f'Selected Value: {size/100}')