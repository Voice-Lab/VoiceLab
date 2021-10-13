import os
import sys
import tkinter
from tkinter import filedialog

def openfiles():
    filename = "/home/david/work/voicelab-gui/voicelab/wizard/toolkits/Voicelab/MeasureMFCCNode.py"
    #root = tkinter.Tk()
    #root.withdraw()
    #listoffiles = filedialog.askopenfilename(title='Select your Node file', defaultextension='py')
    return filename  # listoffiles

def get_command_name(nodefile):
    nodename = nodefile.split("/")[-1].split(".py")[0]

    f = open(nodefile, "r")
    f1 = f.readlines()
    for x in f1:
        if "commmand_name" in x:
            command_name = x[15:]
    assert isinstance(nodename, str)
    return command_name, nodefile, nodename

# Put things in init.py
def add_to_init_py(command_name):
    init_py = '__init__.py'
    with open(init_py, "r") as in_file:
        buf = in_file.readlines()


    with open(init_py, "w") as out_file:
        for line in buf:
            if "Measure" in command_name:
                if "# Measure Nodes" in line:
                    line = line + f'from .{nodename} import {nodename}\n'
                out_file.write(line)
            if "Manipulate" in command_name:
                if "# Manipulate Nodes" in line:
                    line = line + f'from .{nodename} import {nodename}\n'
                out_file.write(line)
            if "Visual" in command_name:
                if "# Visualization Nodes" in line:
                    line = line + f'from .{nodename} import {nodename}\n'
                out_file.write(line)

def add_to_default_settings(command_name, nodename):
    default_settings_file: str = "/home/david/work/voicelab-gui/voicelab/wizard/default_settings.py"
    with open(default_settings_file, "r") as in_file:
        buf = in_file.readlines()

    with open(default_settings_file, "w") as out_file:
        for line in buf:
            if "available_functions =" in line:
                line = line + f'    "{command_name}": Voicelab.{nodename}("{command_name}"),\n'
            out_file.write(line)
        for line in buf:
            if "default_functions = [" in line:
                line = line + f'    "{command_name}",\n'
            out_file.write(line)


if __name__ == '__main__':
    nodefile = sys.argv[1]
    #nodefile = openfiles()
    command_name, nodefile, nodename = get_command_name(nodefile)
    add_to_init_py(command_name)
    add_to_default_settings(command_name[2:-2], nodename)
