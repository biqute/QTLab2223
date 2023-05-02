import numpy as np
import os
import sys

#All the scripts we are going to use are defined in different .py files, in order to make them easier to manage. 
from loadconfiguration import LoadConfiguration
from logconversion import LogConversion
from getspectrafile import GetSpectraFile 
from calcworkpoint import CalcWorkPoint
from findmixcal import FindMixCal
from caliq import Cal_IQ
from backgroundcalibration import BackgroundCalibration
from correctiq import CorrectIQ
from correctiqbackground import CorrectIQBackground

#All our globally defined variables are stored in "globalvariables.py". This ensures the code does not encounter cyclic definition of variables 
#and thus ensures stability.
import globvar

#def ConvertIQ2Af4(run_num, meas_num, spectra_path, iqpath, save_path, iqheader, mode, nch,  datatype):

#Default settings block. Useful in order to debug the code, these should be the argument for the ConvertIQ2Af4 function.
spectra_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Data\\Spectra'
run_num = 34
datatype = 'MixCh'
meas_num = 1
save_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Save'
iqpath = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\IQ' + '\\run' + str(run_num) + '\\'
iqheader = ['IQ0Ch1', 'IQ0Ch2']
nch = 2
mode = 0

#The row below should be the original command, but its argument does not correspond to the log file we want to pick.
#config = loadconfiguration.LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + ".log")
config = LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + '_5785937577' + '.log')

#We modify recordlength and adcconv globally...
globvar.recordlength = float(config[2][1])
globvar.adcconv = float(config[0][1])
samprate = float(config[1][1])
attenuations = [float(config[14][1]) + float(config[15][1])]

#...then we store them in a local variable.
recordlength = globvar.recordlength
adcconv = globvar.adcconv

#Show how data have been arranged
print('Formato dati: ' + str(globvar.dataformat))
print('Lunghezza record: ' + str(globvar.recordlength))

#------------Search for all INPUT----------
#We modify checkpath and logpath globally...
globvar.checkpath = save_path + '\\check_meas' + datatype + str(meas_num)
globvar.logpath = save_path + '\\run' + str(run_num) + '\\' + datatype + str(meas_num) +'.log'

#...then we store them in a local variable. Their content should not be modified later, and the other script
#we will call can retain the value we assigned in the earlier rows by importing the value, now updated as to lines 48 and 49.
logpath = globvar.logpath
checkpath = globvar.checkpath

#Create directories in which store correction results and logs
os.mkdir(save_path)
os.mkdir(save_path + '\\run' + str(run_num))
log = open(logpath, 'a')
log.close()
os.mkdir(checkpath)

globvar.nchan = nch
nchan = globvar.nchan

#For each channel IQ data we declare a proper string
iqfileheader_ch = []
for ii in range(nch):
    iqfileheader_ch.append(iqpath + str(iqheader[ii]))

#Create the list of spectra files. Note we use the symbols "\\" instead of "\" for paths, otherwise it wouldn't work.
data_base_filename = spectra_path + '\\' + 'run' + str(run_num) + '\\'
print('File root: ' + data_base_filename)
file_names = GetSpectraFile(data_base_filename)

if not file_names:
    print('Error: no spectra file found')

#let's see the first and the final file retrieved
print('(file_names) First file: ' + str(file_names[0]))
print('(file_names) Last file: ' + str(file_names[-1]))

#we now want to compute the WorkPoint frequency
posch = np.zeros(nch)
fmeas = np.zeros(nch)
fmeas2 = np.zeros(nch)
cal_mix_file = ([[]]*nch)

for ii in range (nch):
    [posch[ii], fmeas[ii]] = CalcWorkPoint(data_base_filename + file_names[0], recordlength, 2*nch, 2*ii, 2*ii+1, iqfileheader_ch[ii], mode)
    fmeas2[ii] = float(config[10 + ii][1])
    print('Frequency difference for the ' + str(ii) + '-th channel: ' + str(fmeas[ii]-fmeas2[ii]))

    #Find mixer calibration file closest to the frequency working point
    cal_mix_file[ii] = FindMixCal(fmeas[ii], spectra_path + '\\run' + str(run_num), ii + 1)
    print('Signal frequency for the ' + str(ii + 1) + '-th channel probe: ' + str(fmeas[ii]))
    print('Calibration file for the ' + str(ii + 1) + '-th channel mixer: ' + str(cal_mix_file[ii]))

    #Now ALL input are defined. It's possible to create the log file. The function "logconversion" recalls the 
    #matlab script "logconversion2.m" +  probably an updated version of the original "logconversion.m".
    #Refer to "logconversion2.m" for comparision
LogConversion(fmeas, run_num, meas_num, spectra_path, iqpath, iqheader, cal_mix_file, mode, nch, recordlength)