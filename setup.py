#!/usr/bin/env python

from distutils.core import setup
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(name='Voicelab',
      version='1.2.0',
      description='Fully Automated Reproducible Acoustical Analysis',
      long_description = long_description,
      long_description_content_type="text/markdown",
      url= 'https://github.com/Voice-Lab/VoiceLab',
      project_urls={
        "Documentation": "https://voice-lab.github.io/VoiceLab/",
      },
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      author='David Feinberg',
      author_email='feinberg@mcmaster.ca',
      packages=['Voicelab'],
      python_requres=">=3.9",
      install_requires=[
            'numpy',
            'PyQt5',
            'QDarkStyle',
            'praat-parselmouth',
            'librosa',
            'openpyxl',
            'seaborn',
      ]
     )
