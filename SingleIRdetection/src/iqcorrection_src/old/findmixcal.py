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
from displog import DispLog

def FindMixCal(frequency, path, channel):

    file_names = GetSpectraFile(path)
    freqcal = []

    diff = 10e10

    for ii in range(len(file_names)):        
        if(file_names[ii].find('spectra') == -1):
            freqcal.append(float(file_names[ii][-14:-4]))

            if len(freqcal) > 1:
                if freqcal[-1] != freqcal[-2]:
                    if np.abs(freqcal[-1] - frequency) < diff:
                        file = file_names[ii]
                        diff = np.abs(freqcal - frequency)
            else:
                if np.abs(freqcal[-1] - frequency) < diff:
                    file = file_names[ii]
                    diff = np.abs(freqcal[-1] - frequency)

    
    DispLog('- FindMixCal(): OK: frequency difference for the ' + str(channel) + '-th channel and mixer calibration: ' + str(frequency - float(file[-14:-4])))

    return file