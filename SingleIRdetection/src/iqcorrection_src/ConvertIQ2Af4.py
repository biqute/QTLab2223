import numpy as np
import os
import sys

import loadconfiguration as loadc
import logconversion as logc
import getspectrafile as gsf
import calkworkpoint as cwp
import findmixcal as fmc
import caliq as ciq
import backgroundcalibration as bc

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
    background = np.zeros(nch)
    s21xch = np.zeros(nch)
    s21ych = np.zeros(nch)
    f = np.zeros(nch)
    qvalues = np.zeros(nch)

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

        [background[ii], s21xch[ii], s21ych[ii], f[ii], qvalues[ii]] = bc.BackgroundCalibration(iqfileheader_ch[ii], mixer[ii], fmeas[ii])

        #Read and convert the pulse data files
        fmax[ii] = -1000000
        fmin[ii] = 1000000

        amax[ii] = -1000000
        amin[ii] = 1000000


        a[ii] = []
        bufamp[ii] = []
        buffreq[ii] = []
        bufpulse[ii] = []

    original = sys.stdout
    log = open(logpath, 'a')
    sys.stdout = log
    print('\nWritten Files\n')
    sys.stdout = original
    log.close()

    for jj in range(len(file_names)):
        #generate the read file name and open
        fid = open(spectra_path + '/' + file_names[jj])

        #generate the write file name and open
        writefilename = save_path + str(file_names[jj][0:-5]) + '_proc' + str(file_names[jj][-4:-1])

        #Write file on screen and on log file
        fidwrite = open(writefilename, 'w')
        log = open(logpath, 'a')
        print(str(file_names[ii] + str(writefilename)))
        sys.stdout = original
        print(str(file_names[ii] + str(writefilename)))
        log.close()

        npoints = recordlength
        hh = 0

        while True:
            line = fid.radline()

            data = np.fromfile(fid, [2*nch, npoints], dataformat, 0, 'b')

            if str(data):
                #correct for the mixer - first remove the DC offsets.  We could either use
                #the offset IQ scan or use the offsets found from the IQ calibration data
                #5/2^15 is the ADC to volts scaling

                idata = np.zeros(nch)
                qdata = np.zeros(nch)
                a = np.zeros(nch)

                for ii in range(nch):
                    idata[ii] = data[2*ii][:]
                    #Idata{ii} = 5*Idata{ii}(:)/2^15;
                    qdata[ii] = data[2*ii + 1][:]
                    #Qdata{ii} = 5*Qdata{ii}(:)/2^15;

                    if dataformat == 'int16':
                        idata[ii] = np.multiply(adcconv, idata[ii][:]/(2**15))
                        qdata[ii] = np.multiply(adcconv, qdata[ii][:]/(2**15))
                    
                    #apply a correction if it's needed (i.e. mode ~= 0)
                    if mode != 0:
                        [idata[ii], qdata[ii], t[ii]] = shift2pos(Idata{ii},Qdata{ii},IQfileheader_ch{ii},ii,hh,ii,posCh{ii});
                        a[ii] = np.append(a[ii], np.sqrt(t[ii][0]**2 + t[ii][1]**2))



    

    
    


