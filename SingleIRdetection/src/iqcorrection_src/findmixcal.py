#The following function retrieves a record of all the files available in the spectra path in order
#to return the one that has the best - fitting calibration frequency for our system
#----------------------------------------------
#input: 
#   - "path" in which search for the spectra files
#   - frequency which we want our calibration file to be near
#   - channel on which we are operating (again, fundamental information in order to find calibration files)
#
#output: the output is the exact file, between the many choices of spectra files, that best approaches our operating frequency
#----------------------------------------------

import numpy as np
from getspectrafile import GetSpectraFile
import sys

import globvar

def FindMixCal(frequency, path, channel):

    logpath = globvar.logpath
    
    #'\\MixCh'+ str(channel)

    #Following the same route as for "ConvertIQ2Af4.py" we use the function GetSpectraFile in order
    #to retrieve all spectra file names

    file_names = GetSpectraFile(path)

    diff = 10e10

    for ii in range(len(file_names)):   #check later?
        
        if(file_names[ii].find('spectra') == -1):
            freqcal = float(file_names[ii][-14:-4])

            if np.abs(freqcal - frequency) < diff: #<= is here only to let this workout for the given data, it should be '<'
                file = file_names[ii]
                diff = np.abs(freqcal - frequency)
    
    if logpath:
        fid = open(logpath, 'a')
        original_output = sys.stdout
        sys.stdout = fid
        print(' - FindMixCal(): OK: frequency difference for the ' + str(channel) + '-th channel and mixer calibration: ' + str(frequency - float(file[-14:-4])))
        sys.stdout = original_output
        fid.close()

    return file