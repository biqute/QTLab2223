import numpy as np
import os
import sys

import globalvariables
import loadconfiguration
import logconversion
import getspectrafile 
import calcworkpoint
import findmixcal as fmc
import caliq as ciq
import backgroundcalibration as bc
import correctiq
import correctiqbackground

#def ConvertIQ2Af4(run_num, meas_num, spectra_path, iqpath, save_path, iqheader, mode, nch,  datatype):

#Default settings block. Useful in order to debug the code.
spectra_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Data\\Spectra'
run_num = 34
datatype = 'MixCh'
meas_num = 1
save_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Save'
iqpath = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\IQ'
iqheader = ['IQ0Ch1off', 'IQ0Ch2off']
nch = 2
mode = 0

global dataformat
dataformat = 'int16'
global recordlength
global adcconv

#The row below should be the original command, but its argument does not correspond to the log file we want to pick.
#config = loadconfiguration.LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + ".log")
config = loadconfiguration.LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + '_5785937577' + '.log')

recordlength = float(config[2][1])
adcconv = float(config[0][1])
samprate = float(config[1][1])
attenuations = [float(config[14][1]) + float(config[15][1])]

#Show how data have been arranged
print('Formato dati: ' + str(dataformat))
print('Lunghezza record: ' + str(recordlength))

#------------Search for all INPUT----------

global checkpath
global logpath

#Create directories in which store correction results and logs
os.mkdir(save_path)
os.mkdir(save_path + '\\run' + str(run_num))
checkpath = save_path + '\\check_meas' + datatype + str(meas_num)
logpath = globalvariables.logpath
log = open(logpath, 'a')
log.close()
os.mkdir(checkpath)


global nchan
nchan = nch

#For each channel IQ data we declare a proper string
iqfileheader_ch = []
for ii in range(nch):
    iqfileheader_ch.append(iqpath + str(iqheader[ii]))

#Create the list of spectra files. Note we use the symbol "/" instead of "\" for paths otherwise it wouldn't work
data_base_filename = spectra_path + '\\' + 'run' + str(run_num) + '\\'
print('File root: ' + data_base_filename)
file_names = getspectrafile.GetSpectraFile(data_base_filename)

if not file_names:
    print('Error: no spectra file found')

#let's see the first and the final file retrieved
print('First file: ' + str(file_names[0]))
print('Last file: ' + str(file_names[-1]))

#we now want to compute the WorkPoint frequency
posch = np.zeros(nch)
fmeas = np.zeros(nch)
fmeas2 = np.zeros(nch)
cal_mix_file = np.zeros(nch)

for ii in range (nch):
    [posch[ii], fmeas[ii]] = calcworkpoint.CalcWorkPoint(spectra_path +  file_names[0] +  recordlength[1 + 1] +  2*nch +  2*ii-1 +  2*ii +  iqfileheader_ch[ii] +  mode)
    fmeas2[ii] = float(config[9 + ii][2])
    print('Frequency difference for the ' + str(ii) + '-th channel: ' + str(fmeas(ii)-fmeas2(ii)))

    #Find mixer calibration file closest to the frequency working point
    cal_mix_file[ii] = fmc.FindMixCal(fmeas(ii) + spectra_path + ii)
    print('Signal frequency for the ' + str(ii) + '-th channel probe: ' + str(fmeas(ii)))
    print('Calibration file for the ' + str(ii) + '-th channel mixer: ' + str(cal_mix_file))

    #Now ALL input are defined. It's possible to create the log file. The function "logconversion" recalls the 
    #matlab script "logconversion2.m" +  probably an updated version of the original "logconversion.m".
    #Refer to "logconversion2.m" for comparision
logconversion.LogConversion(fmeas, run_num, meas_num, spectra_path, iqpath, iqheader, cal_mix_file, mode, nch, recordlength)