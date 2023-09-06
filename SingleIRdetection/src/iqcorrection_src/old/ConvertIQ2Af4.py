import numpy as np
import os
import sys
from matplotlib import pyplot as plt

#All the scripts we are going to use are defined in different .py files, in order to make them easier to manage. 
from loadconfiguration import LoadConfiguration
from logconversion import LogConversion
from getspectrafile import GetSpectraFile 
from calcworkpoint import CalcWorkPoint
from findmixcal import FindMixCal
from caliq import Cal_IQ
from shift2pos import Shift2Pos
from backgroundcalibration import BackgroundCalibration
from correctiq import CorrectIQ
from findiqcorrection import Background
from correctiqbackground import CorrectIQBackground
from readdata import ReadData

#All our globally defined variables are stored in "globalvariables.py". This ensures the code does not encounter cyclic definition of variables 
#and thus ensures stability.
import globvar

#def ConvertIQ2Af4(run_num, meas_num, spectra_path, iqpath, save_path, iqheader, mode, nch,  datatype):

#Default settings block. Useful in order to debug the code, these should be the argument for the ConvertIQ2Af4 function.
spectra_path = '/home/alessandro/Lab/Correction/Spectra/'
run_num = 34
datatype = 'MixCh'
meas_num = 1    
save_path = '/home/alessandro/Lab/Correction/Save'
iqpath = '/home/alessandro/Lab/Correction/' + 'run' + str(run_num) + '/'
iqheader = ['IQ0Ch1', 'IQ0Ch2']
nch = 2
mode = 0
ifplot = 1

#The row below should be the original command, but its argument does not correspond to the log file we want to pick.
#config = loadconfiguration.LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + ".log")
config = LoadConfiguration(spectra_path + "\\run" + str(run_num) + '\\' + datatype + str(meas_num) + '_5785937577' + '.log')

#We modify recordlength and adcconv globally...
globvar.recordlength = float(config[2][1])
globvar.adcconv = float(config[0][1])
samprate = float(config[1][1])
attenuations = [float(config[14][1]) + float(config[15][1])]
dataformat = globvar.dataformat

#...then we store them in a local variable.
recordlength = int(globvar.recordlength)
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
spectra_path_run = spectra_path + '\\' + 'run' + str(run_num) + '\\'
print('File root: ' + spectra_path_run)
file_names = GetSpectraFile(spectra_path_run)
print(file_names)

if not file_names:
    print('Error: no spectra file found')

#Let's see the first and the final file retrieved
print('(file_names) First file: ' + str(file_names[0]))
print('(file_names) Last file: ' + str(file_names[-1]))

#We now want to compute the WorkPoint frequency
posch = np.zeros(nch)
fmeas = np.zeros(nch)
fmeas2 = np.zeros(nch)
cal_mix_file = ([[]]*nch)

for ii in range (nch):
    [posch[ii], fmeas[ii]] = CalcWorkPoint(spectra_path_run + file_names[0], recordlength, 2*nch, 2*ii, 2*ii+1, iqfileheader_ch[ii], mode, ifplot)
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

mixercalfile_ch = []
mixer = []
background = []
tempx = [] #to append the outputs of BackgroundCalibration...
tempy = [] 
tempf = []
qvalues = np.zeros([2, 4])

fmax = np.zeros(nch)
fmin = np.zeros(nch)
amax = np.zeros(nch)
amin = np.zeros(nch)
a = np.zeros(nch, dtype = object)
bufamp = np.zeros(nch, dtype = object)
buffreq = np.zeros(nch, dtype = object)
bufpulse = np.zeros(nch, dtype = object)

for ii in range(nch):
    #Create the string path for mixercalibration. The "ii-th" entry of the
    #object "mixercalfile_ch" is the path to the calibration file for the
    #"ii-th" channel

    mixercalfile_ch.append(spectra_path + '\\run' + str(run_num) + '\\' + cal_mix_file[ii])

    #--------- Begin the IQ loop calibration --------#

    #First we characterize the loop, i.e. we find the parameters that best describe our non - ideal IQ mixer
    mixer.append(Cal_IQ(mixercalfile_ch[ii], 2*nch, 2*ii, 2*ii+1, 1, cal_mix_file[ii], nch))
    
    #Fit the mixer calibration data file and find the coefficients used for the correction

    #Fit the background and return the fixed IQ loop

    [back, xchs, ychs, f, qvalues[ii][0], qvalues[ii][1], qvalues[ii][2], qvalues[ii][3]] = BackgroundCalibration(iqfileheader_ch[ii], mixer[ii], fmeas[ii], ifplot)
    #[background[ii], s21xch[ii], s21ych[ii], f[ii], qvalues[ii]] = BackgroundCalibration(iqfileheader_ch[ii], mixer[ii], fmeas[ii], ifplot)
    #qvalues stores values in a way such that the row is the channel and the column is one of the four qvalues entries for that channel

    background.append(back)
    tempx.append(xchs)
    tempy.append(ychs)
    tempf.append(f)

    #Read and convert the pulse data files
    fmax[ii] = -1000000
    fmin[ii] = 1000000
    amax[ii] = -1000000
    amin[ii] = 1000000

s21xch = np.array(tempx)
s21ych = np.array(tempy)
f = np.array(tempf)

original = sys.stdout
log = open(logpath, 'a')
sys.stdout = log
print('\nWritten Files\n')
sys.stdout = original
log.close()

npoints = int(globvar.recordlength)
idata = []
qdata = []

a = np.zeros(nch)
pulse_data = np.zeros([nch, 2])
mapped_pulse_data = np.zeros([nch, 2])
amplitude_signal = np.zeros([nch, 2])
frequency_signal = np.zeros([nch, 2])
t = np.zeros(nch)

for jj in rangelen(file_names):
    #generate the read file name and open. We don't want to open the .00 file!
    filefid = spectra_path + '\\run' + str(run_num) + '\\' + file_names[jj]
    fid = open(filefid)

    #generate the write file name and open
    writefilename = save_path + str(file_names[jj][0:-5]) + '_proc' + str(file_names[jj][-4:-1])

    #Write file on screen and on log file
    fidwrite = open(writefilename, 'w')
    log = open(logpath, 'a')
    #print(str(file_names[ii] + str(writefilename)))
    sys.stdout = original
    #print(str(file_names[ii] + str(writefilename)))
    log.close()

    hh = 0

    #while True:
        #line = fid.readline()

    data = np.loadtxt(filefid, dtype = dataformat, delimiter = '\t')

    if str(data):
        #correct for the mixer - first remove the DC offsets.  We could either use
        #the offset IQ scan or use the offsets found from the IQ calibration data
        #5/2^15 is the ADC to volts scaling

        for ii in range(nch):
            [array1, array2] = ReadData(filefid, 2*nch, 2*ii, 2*ii + 1, 'start', npoints)
            idata = np.hstack([idata, array1])  #I chose this route because of incongruencies of the files given to us. Recordlength was actually greater
            qdata = np.hstack([qdata, array2])  #than the number of points from data
            #Idata{ii} = 5*Idata{ii}(:)/2^15;
            #Qdata{ii} = 5*Qdata{ii}(:)/2^15;

            if dataformat == 'int16':
                idata[:][ii] = adcconv*idata[:][ii]/(2**15)
                qdata[:][ii] = adcconv*qdata[:][ii]/(2**15)
            
            #Apply a correction if it's needed (i.e. mode ~= 0)
            if mode != 0:
                [idata[:][ii], qdata[:][ii], t[:, ii]] = Shift2Pos(idata[:][ii], qdata[:][ii], iqfileheader_ch[ii], ii, hh, ii, posch[ii], ifplot)
                a[:, ii] = np.append(a[ii], np.sqrt(t[0, :]**2 + t[1, :]**2))   #i think this should be fixed, don't think "a" is properly declared...

            idata[ii] = idata[ii] - background[ii].I0
            qdata[ii] = qdata[ii] - background[ii].Q0

            #Now correct for the mixer gains and phase errors
            [idata[:][ii], qdata[:][ii]] = CorrectIQ(idata[:][ii], qdata[:][ii], mixer[ii])

            #Then apply the background correction
            pulse_data[ii][:] = CorrectIQBackground(fmeas[ii]*np.ones(np.size(idata[:][ii])), complex(idata[:][ii], qdata[:][ii]), background[:][ii])
            
            #Next apply the rotations, as applied to the IQ loop
            pulse_data[ii][:] = 1 - np.cos(background[ii].LoopRotation)*np.exp(-1j*background[ii].LoopRotation)*(1 - (pulse_data[ii]*np.exp(-1j * background[ii].OverallRotation)))
        
            #now we can convert the timestream data into frequency and dissipation signals
            #through the transformation S_21_mapped = 1 / 1 - S21
            mapped_pulse_data[ii][:]= 1/(1 - pulse_data[ii][:])
            amplitude_signal[ii][:] = np.real(mapped_pulse_data[ii][:])
            frequency_signal[ii][:] = np.imag(mapped_pulse_data[ii][:])

                    '''
                    if ifplot && hh<5;
                        figure
                        subplot(4,1,1:2);
                        plot( real(pulse_data{ii}) ,imag(pulse_data{ii}),'r')
                        hold on
                        plot(S21xch{ii},S21ych{ii})
                        subplot(4,1,3);
                        plot(amplitude_signal{ii});
                        subplot(4,1,4);
                        plot(frequency_signal{ii})
                        
                        close all
                    end
                    %              mapped_pulse_data1 = 1 ./ (1 - pulse_data1);
                    %             amplitude_signal1 = real( mapped_pulse_data1).*(curve1.a/curve1.b);
                    %             frequency_signal1 = imag( mapped_pulse_data1).*(curve1.a/curve1.b);
                    %             mapped_pulse_data2 = 1 ./ (1 - pulse_data2);
                    %             amplitude_signal2 = real( mapped_pulse_data2)*(curve2.a/curve2.b);
                    %             frequency_signal2 = imag( mapped_pulse_data2)*(curve2.a/curve2.b);
                    
                    %write this data to the new file
                    '''
                buff = []
            
                for ii in range(nch):
                    buff = np.append(buff, amplitude_signal[ii], frequency_signal[ii])
        
                sys.stdout = fidwrite
                data = print(fidwrite, buff, 'double')
                
                for ii in range(nch)
                    #look for max and min of the pulse
                    loc = np.max(frequency_signal[ii])

                if (loc > fmax[ii]):
                    fmax[ii] = loc
                
                
                loc = np.max(amplitude_signal[ii])
                if (loc > amax[ii]):
                    amax[ii] = loc
            
                loc = np.min(amplitude_signal[ii])
                if (loc < amin[ii]):
                    amin[ii] = loc
                
                loc = np.min(frequency_signal[ii])
                if (loc < fmin[ii]):
                    fmin[ii] = loc
            
                #signal to print
                if (hh < 5 and ii < 3):
                    bufamp = np.append(bufamp, amplitude_signal[ii].T)
                    buffreq = np.append(buffreq, frequency_signal[ii].T)
                    bufpulse = np.append(bufpulse, pulse_data[ii])
        
        fid.close()
        fidwrite.close()

    original = sys.stdout
    log = open(logpath, 'a')
    print('\n----- DATA----')

    for ii in range(nch):
        print('\n\nRESONANCE CH' + str[ii] + ' DATA')
        print('\nQUALITY FACTORS AND FREQUENCY\n')
        print(' \nQ_TOT = ' + str(qvalues[ii][0]) + '\nf0 = ' + str(qvalues[ii][1]) + '\nQi = ' + str(qvalues[ii][2]) + '\nQc = ' + str(qvalues[ii][3]))
        print('OTHER DATA\n')
        print('\nCh ' + str(ii) + 'Working point frequency ' + str(fmeas[ii]))
        print('\nCh ' + str(ii) + 'Frequency range ' + str(fmin[ii]) + ' <-> ' + str(fmax[ii]))
        print('\nCh ' + str(ii) + 'Amplitude range ' + str(amin[ii]) + ' <-> ' + str(amax[ii]))
        print('\nCh ' + str(ii) + 'correction ' + str(np.mean(a[ii])) + ' + / - ' + str(np.std(a[ii], 0)))

    print('\nshiftmins = ' + str(amin[0]) + str(fmin[0]) + str(amin[1]) + str(fmin[1]))
    print('\nshiftmaxs = ' + str(amax[0]) + str(fmax[0]) + str(amax[1]) + str(fmax[1]))
    log.close()

    numfiles = len(file_names)
    np.save()
    numfiles = length(file_names)
    save([str(save_path) + '/run' + str(run_num) + datatype + str(meas_num) + '.mat'],'Qvalues','fmeas','run_num','meas_num','spectra_path','IQ_path','IQheader','cal_mix_file','mode','Nch','Recordlength','numfiles','ADCconv','SampRate','Attenuations')
    exts = ['.pdf', '.png']
    cmds = ['-dpdf', '-dpng']

    '''              
    for ii=1:Nch
    for i=1:length(exts);

    kl=figure;




    plot(f{ii},sqrt(S21xch{ii}.^2+S21ych{ii}.^2));
    legend('S21 real');
    xlabel('Frequency');
    ylabel('quadraqture');
    print(kl,cmds{i},[checkpath,'/ResonanceCh',num2str(ii),exts{i}]);

    kt=figure;




    plot(f{ii},atan(S21ych{ii}./S21xch{ii}));
    legend('S21 imaginary');
    xlabel('Frequency');
    ylabel('phase');
    print(kt,cmds{i},[checkpath,'/ResonanceCh',num2str(ii),exts{i}]);







    kk=figure;

    plot( real( bufPulse{ii}) ,imag( bufPulse{ii}),'g');
    hold on
    plot(S21xch{ii},S21ych{ii},'r');
        hold on
    plot(S21xch{ii}(1),S21ych{ii}(1),'o');

    legend('Ch1 data','S21 corr','Low freq');
    xlabel('I normalized units');
    ylabel('Q normalized units');
    print(kk,cmds{i},[checkpath,'/CircleCh',num2str(ii),exts{i}]);

    %%

    if 0
        a=figure;
        plot( (1:length(amplitude_signal1)), amplitude_signal1);
        title('Amplitude ch1')
        grid
        legend('Amplitude');
        xlabel('Number of points');
        ylabel('Amplitude');
        print(a,cmds{i},[checkpath,'/PulseAmpch1',exts{i}]);
        
        
        b=figure;
        plot( (1:length(frequency_signal1)), frequency_signal1);
        title( 'Frequency ch1');
        grid
        legend('Amplitude');
        xlabel('Number of points');
        ylabel('Amplitude');
        print(b,cmds{i},[checkpath,'/PulseFreqch1',exts{i}]);
        
        
        
        ll=figure;
        plot( (1:length(amplitude_signal1)), amplitude_signal1,'r');
        title( 'Data Af Ch1')
        
        xlabel('Number of points');
        ylabel('Amplitude');
        
        
        hold on
        
        
        plot( (1:length(frequency_signal1)), frequency_signal1)
        
        grid
        legend('Amplitude','Frequency Amplitude');
        xlabel('Number of points');
        ylabel('Amplitude');
        print(ll,cmds{i},[checkpath,'/PulseFreqch1',exts{i}]);
        
    end



    ler=figure;
    [AX,H1,H2] = plotyy((1:length(bufAmp{ii})), bufAmp{ii},1:length(bufFreq{ii}), bufFreq{ii});
    title( ['Data Af Ch',num2str(ii)]);
    set(H1,'LineStyle','--')
    xlabel('Number of points');
    ylabel('Amplitude');
    scale1setmin=max( bufAmp{ii})-2*(max( bufAmp{ii})-min( bufAmp{ii}));
    scale1setmax=max( bufAmp{ii})+0.3*(max( bufAmp{ii})-min( bufAmp{ii}));
    scale1setStep=(max(bufAmp{ii})-min( bufAmp{ii}))/5;
    scale2setmin=min( bufFreq{ii})-0.1*(max( bufFreq{ii})-min(bufFreq{ii}));
    scale2setmax=min( bufFreq{ii})+2.2*(max(bufFreq{ii})-min( bufFreq{ii}));
    scale2setStep=(max(bufFreq{ii})-min( bufFreq{ii}))/5;

    set(AX(1),'YLim',[scale1setmin,scale1setmax]);
    set(AX(1),'YTick',[scale1setmin:scale1setStep:scale1setmax]);
    set(AX(2),'YLim',[scale2setmin scale2setmax]);
    set(AX(2),'YTick',[scale2setmin:scale2setStep:scale2setmax]);
    grid
    legend('Amplitude','Frequency Amplitude')
    print(ler,cmds{i},[checkpath,'/PulseCh',num2str(ii),exts{i}]);



    end
    end


    disp('---------------End Conversion---------------------------------------------')
    % writenm=[save_path,'/RunStat'];
    % state=[meas_num curve1.a C1(:,1)' curve1.b C1(:,2)' curve1.c C1(:,3)'...
    %     curve2.a C2(:,1)' curve2.b C2(:,2)' curve2.c C2(:,3)' fmeas1 fmeas2]
    % 
    % dlmwrite(writenm, state, '-append')
    '''
    return
                        
                        


