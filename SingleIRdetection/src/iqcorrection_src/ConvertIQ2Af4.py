import numpy as np

import loadconfiguration as loadc
import logconversion as logc
import getspectrafile as gsf
import calkworkpoint as cwp
import findmixcal as fmc
import caliq as ciq
import os

def ConvertIQ2Af4(run_num, meas_num, spectra_path, iqpath, save_path, iqheader, mode, nch,  datatype):

    global dataformat
    dataformat = 'int16'
    global recordlength
    global  adcconv

    config = loadc.LoadConfiguration(spectra_path + "/run" + str(run_num) + datatype + str(meas_num) +".log")

    recordlength = float(config[3][2])
    adcconv = float(config[1][2])
    samprate = float(config[2][2])
    attenuations = [float(config[15][2]) + float(config[16][2])]

    #show how data have been arranged

    print('Formato dati: ' + str(dataformat))
    print('Lunghezza record ' + str(recordlength))

    #------------Search for all INPUT----------

    global checkpath
    checkpath = save_path + r'\check_meas' + datatype + str(meas_num)
    global logpath
    logpath = save_path + r'\run' + str(run_num) + datatype + str(meas_num) +'.log'
    
    global nchan
    nchan = nch

    #create directories in which data will be stored
    os.mkdir(save_path)
    os.mkdir(checkpath)

    #for each channel IQ data we declare a proper string
    iqfileheader_ch = []
    for ii in range(nch):
        iqfileheader_ch.append(iqpath + str(iqheader[ii]))
        i = i + 1

    #create the list of spectra files. Note we use the symbol "/" instead of "\" for paths otherwise it wouldn't work
    data_base_filename = spectra_path + 'r\run' + str(run_num) + datatype + str(meas_num) + '.'
    print('File root: ' + data_base_filename)
    file_names = gsf.GetSpectraFile(data_base_filename)

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
        [posch[ii], fmeas[ii]] = cwp.CalkWorkPoint(spectra_path +  file_names[0] +  recordlength[1 + 1] +  2*nch +  2*ii-1 +  2*ii +  iqfileheader_ch[ii] +  mode)
        fmeas2[ii] = float(config[9 + ii][2])
        print('Frequency difference for the ' + str(ii) + '-th channel: ' + str(fmeas(ii)-fmeas2(ii)))

        #Find mixer calibration file closest to the frequency working point
        cal_mix_file[ii] = fmc.FindMixCal(fmeas(ii) + spectra_path + ii)
        print('Signal frequency for the ' + str(ii) + '-th channel probe: ' + str(fmeas(ii)))
        print('Calibration file for the ' + str(ii) + '-th channel mixer: ' + str(cal_mix_file))

        #Now ALL input are defined. It's possible to create the log file. The function "logconversion" recalls the 
        #matlab script "logconversion2.m" +  probably an updated version of the original "logconversion.m".
        #Refer to "logconversion2.m" for comparision
    logc.logconversion(fmeas, run_num, meas_num, spectra_path, iqpath, iqheader, cal_mix_file, mode, nch, recordlength)

    mixercalfile_ch = []
    mixer = []

    for ii in range(nch)
        #Create the string path for mixercalibration. The "ii-th" entry of the
        #object "mixercalfile_ch" is the path to the calibration file for the
        #"ii-th" channelà

        mixercalfile_ch.append(spectra_path + '/' + cal_mix_file[ii])

        #---------Begin the IQ loop calibration--------#

        #First we characterize the loop, i.e. we find the parameters that best
        #describe our non-ideal IQmixer

        mixer.append(ciq.Cal_IQ(mixercalfile_ch[ii], 2*nch, 2*ii-1, 2*ii, 1, cal_mix_file[ii]))
        
        #Fit the mixer calibration data file and find the coefficients used for the correction

        #Fit the background and return the fixed IQ loop

        [background[ii], S21xch[ii], S21ych[ii], f[ii], Qvalues[ii]] = background_calibrationsc(IQfileheader_ch{ii}, mixer(ii), fmeas(ii));



    
    


