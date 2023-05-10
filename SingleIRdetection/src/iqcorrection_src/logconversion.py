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

import globvar

def LogConversion(fmeas, run_num, meas_num, spectra_path, iqpath, iqheader, cal_mix_file, mode, nch, recordlength):
    
    logname = globvar.logpath        
    fid = open(logname, 'a')
    original_stdout = sys.stdout
    sys.stdout = fid 
    
    print('Run: ' + str(run_num) + '| Measure number: ' + str(meas_num))
    print('Number of channels: ' + str(nch))
    print('Record length: ' + str(recordlength))
    print('IQ path: ' + str(iqpath))
    print('Spectra path: ' + str(spectra_path))
    print('Correction mode: ' + str(mode))
          
    for ii in range(nch):
        print('-------Ch' + str(ii) + ' settings-------')
        print('Mixer calibration: ' + str(cal_mix_file[ii]))
        print('IQ header: ' + str(iqheader[ii]))
        print('Frequency: ' + str(fmeas[ii]))

    print('CHECKS: ') #(?)
    sys.stdout = original_stdout
    fid.close()