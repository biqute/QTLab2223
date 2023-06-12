import os
import sys
import numpy as np
import globvar
from displog import DispLog

# Return a list of the files contained in the 'key' path. If no file is found, returns an empty array.
    # Argument:
    # - key -> the path of which we want to list the content
    # If there is only one file in the key path, the function only returns the name of that file instead of a list containing it.

def GetSpectraFile(key):

    logpath = globvar.logpath
    out = []
    original = sys.stdout

    #We want a list of all the files contained in the directory at 'key'. As default, the command 'os.listdir' returns a list of all the files.
    list = os.listdir(key)

    i = 0
    k = 0
    nonnull = 0
    out = []

    for i in range(len(list)):
        if((list[i].find('.txt') != -1) and list[i].find('spectra') != -1):
            out.append(list[i])
        
    if out:
        DispLog('- GetSpectraFile(): OK: Spectra files found: ' + str(key) +'\n')
    else:
        DispLog('- GetSpectraFile(): ERROR: No spectra files found: ' + str(key) + '\n')
        out = []
        return 

    if len(out) == 1:
        output = out[0]
    else:
        output = out

    return output