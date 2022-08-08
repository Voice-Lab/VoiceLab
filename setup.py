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
      packages=setuptools.find_packages(),
      python_requres=">=3.9",
      install_requires=[
            'numpy==1.22',
            'PyQt5==5.15.2',
            'QDarkStyle==2.8.1',
            'praat-parselmouth==0.4.1',
            'librosa==0.9.2',
            'openpyxl==3.0.6',
            'seaborn==0.11.1',
      ]
     )
