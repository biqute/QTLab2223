import numpy as np
import os
import sys

import loadconfiguration
import logconversion as logc
import getspectrafile as gsf
import calkworkpoint as cwp
import findmixcal as fmc
import caliq as ciq
import backgroundcalibration as bc
import correctiq
import correctiqbackground

def ConvertIQ2Af4(run_num, meas_num, spectra_path, iqpath, save_path, iqheader, mode, nch,  datatype):

    global dataformat
    dataformat = 'int16'
    global recordlength
    global  adcconv

    config = loadconfiguration.LoadConfiguration(spectra_path + "/run" + str(run_num) + datatype + str(meas_num) + ".log")

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
                pulse_data = np.zeros(nch)
                mapped_pulse_data = np.zeros(nch)
                amplitude_signal = np.zeros(nch)
                frequency_signal = np.zeros(nch)

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
                        [idata[ii], qdata[ii], t[ii]] = shift2pos(Idata{ii}, Qdata[ii], iqfileheader_ch[ii], ii, hh, ii, posch[ii])
                        a[ii] = np.append(a[ii], np.sqrt(t[ii][0]**2 + t[ii][1]**2))

                    idata[ii] = idata[ii] - background[ii].i0
                    qdata[ii] = qdata[ii] - background[ii].q0

                    #now correct for the mixer gains and phase errors
                    [idata[ii], qdata[ii]] = correctiq.CorrectIQ(idata[ii], qdata[ii], mixer[ii])
                
                    #then apply the background correction
                    pulse_data[ii] = correctiqbackground.CorrectIQBackground(fmeas[ii]*np.ones(np.size(idata[ii])), complex(idata[ii], qdata[ii]), background[ii])
                    
                    
                    #next apply the rotations as applied to the IQ loop
                    pulse_data[ii] = 1 - np.multiply(np.multiply(np.cos(background[ii].LoopRotation), np.exp( -1j*background[ii].LoopRotation)), (1 - np.multiply(pulse_data[ii], np.exp(-1j * background[ii].OverallRotation))))
                
                    #now we can convert the timestream data into frequency and dissipation signals
                    #through the transformation S_21_mapped = 1 / 1 - S21
                    mapped_pulse_data[ii]= np.divide(1, (1 - pulse_data[ii]))
                    amplitude_signal[ii] = np.real(mapped_pulse_data[ii])
                    frequency_signal[ii] = np.imag(mapped_pulse_data[ii])

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
                        
                        


