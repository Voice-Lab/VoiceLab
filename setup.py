#!/usr/bin/env python

from distutils.core import setup
import setuptools

setup(name='Voicelab',
      version='1.01',
      description='Python GUI for working with voicefiles',
      author='David Feinberg',
      author_email='feinberg@mcmaster.ca',
      packages=['Voicelab'],
      install_requires=[
            'qdarkstyle',
            'praat-parselmouth',
            'crepe',
            'openpyxl',
            'PyQt5==5.9.2',
            'pandas',
            'seaborn',
            'tensorflow'
      ]
     )
