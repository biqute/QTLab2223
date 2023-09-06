#The following function writes the result of some of the operations that took place in 
#"ConvertIQ2Af4.py". It writes everything noteworth inside a log file.
#----------------------------------------------
#input: 
#   - fmeas
#   - run_num is the number of the run
#   - meas_nume is the number of the measurement
#   - spectra_path is the path to the spectra files
#   - iqpath is the path to the iq data files
#   - iqheader
#   - cal_mix_file is the path to the calibration file for the iqmixer
#   - mode stands for the mode we chose for calibration
#   - nch is the channel number
#   - recordlength is the measurement length
#output: None
#----------------------------------------------

import sys
import os
from displog import DispLog

def LogConversion(fmeas, run_num, meas_num, spectra_path, iqpath, iqheader, cal_mix_file, mode, nch, recordlength):

    DispLog('Run: ' + str(run_num) + '| Measure number: ' + str(meas_num))
    DispLog('Number of channels: ' + str(nch))
    DispLog('Record length: ' + str(recordlength))
    DispLog('IQ path: ' + str(iqpath))
    DispLog('Spectra path: ' + str(spectra_path))
    DispLog('Correction mode: ' + str(mode))
          
    for ii in range(nch):
        DispLog('-------Ch' + str(ii + 1) + ' settings-------')
        DispLog('Mixer calibration: ' + str(cal_mix_file[ii]))
        DispLog('IQ header: ' + str(iqheader[ii]))
        DispLog('Frequency: ' + str(fmeas[ii]))

    DispLog('CHECKS: ')