#!/usr/bin/env python

from distutils.core import setup
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(name='Voicelab',
      version='1.0297',
      description='Python GUI for working with voicefiles',
      long_description = long_description,
      long_description_content_type="text/markdown",
      url= 'https://github.com/Voice-Lab/VoiceLab',
      author='David Feinberg',
      author_email='feinberg@mcmaster.ca',
      packages=['Voicelab'],
      install_requires=[
            'numpy==1.22.0',
            'PyQt5==5.15.2',
            'QDarkStyle==2.8.1',
            'praat-parselmouth==0.4.0',
            'librosa==0.8.0',
            'openpyxl==3.0.6',
            'seaborn==0.11.1',
      ]
     )
