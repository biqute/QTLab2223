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
import getspectrafile as gsf
def FindMixCal(frequency, path, channel):
    data_base_filename = path + 'MixCh'+ str(channel)

    #Following the same rout as for "ConvertIQ2Af4.py" we use the function GetSpectraFile in order
    #to retrieve all spectra file names

    file_names = gsf.GetSpectraFile(data_base_filename)

    diff = 10e10
    for ii in range(len(file_names)):
        freqcal = float(file_names[ii][-13:-4])

        if np.abs(freqcal - frequency) < diff:
            file = file_names[ii]
            diff = np.abs(freqcal - frequency)
        
    print(' - FindMixCal(): OK: frequency difference for the ' + str(channel) + '-th channel and mixer calibration: ' + str(frequency - float(file[-13:-4])))
    return file