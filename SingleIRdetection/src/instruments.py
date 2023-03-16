# Contributo alla libreria che stiamo scrivendo per parlare con gli strumenti

#fai funzione che manda mail se temperatura va oltre tot
import pyvisa
import numpy as np
import time
import smtplib, ssl
from matplotlib import pyplot as plt
import struct
from PyDAQmx import TaskHandle, byref, int32, DAQmxCreateTask, DAQmxCreateAIVoltageChan, DAQmxCfgSampClkTiming, DAQmxStartTask, DAQmx_Val_Cfg_Default, DAQmx_Val_Rising, DAQmx_Val_Volts, DAQmx_Val_FiniteSamps, DAQmxReadAnalogF64, DAQmx_Val_GroupByChannel, DAQError, DAQmxStopTask, DAQmxClearTask
import h5py
import cv2
from PIL import Image

#with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#server.login("mail@gmail.com", password)



def measure(fridge, vna, temps, format_data, plot = 's21module'):
    '''Outputs two matrices with dimensions num_points vs num_temperatures.
    The first contains the i values while the second contains the q values.'''

    f = np.array(vna.freqs)
    num_points = vna.points
    s21_module = np.zeros((len(temps), num_points))
    I = np.zeros((len(temps), num_points))
    Q = np.zeros((len(temps), num_points))

    h = h5py.File('find_freqs.h5', 'w')

    numtemps = len(temps)

    for k in range(numtemps): 
        fridge.set_T(int(temps[k]))
        time.sleep(30)
        ok = fridge.check_stability(temps[k], 1)
        
        if ok == True:
            i, q = vna.get_data(format_data)
            I[k,:] = i
            Q[k,:] = q           
            
        elif ok == False:
            print ('I had some trouble with the stability of temperature ' + str(temps[k]))
            vna.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it"],"Temperature not stable","I had some trouble with the stability of temperature " + str(temps[k]) + "Do something plis.")
            k = numtemps + 1       
        
        n = 'temp_' + str(temps[k]) + 'mK'        
        if plot == 's21module':
            s21_module[k,:] = np.power((np.power(q, 2) + np.power(i, 2)), 1/2)                               #we compute s21 module starting from data
            s21_module[k,:] = s21_module[k,:]/max(s21_module[k,:])                                      #we normalize s21 module (just a convenction)
            plt.plot(f, s21_module[k,:])
            plt.savefig('plots/resonance_plot_'+str(n)+'.jpg', dpi=1000)
            plt.clf()

        #now we save the data
        hfdat = h.create_group(str(n))
        hfdat_i = hfdat.create_dataset(name = 'I_' + str(n), data = i)
        hfdat_q = hfdat.create_dataset(name = 'Q_' + str(n), data = q)
        hfdat_f = hfdat.create_dataset(name = 'freq_' + str(n), data = f)

        image = cv2.imread('plots/resonance_plot_'+str(n)+'.jpg')  # reads the created .jpg as array 
        hfdat_plot = hfdat.create_dataset(name = 'plot_' + str(n), data = image)
        
        print('Data saved' + str(k))
    
    return f, I, Q



def measuref(fridge, vna, temps, freqs_ranges, format_data):        #the argument freqs is a matrix, or better an array of arrays, each of witch has 2 elements: a start and stop frequency
    '''Outputs two matrices with dimensions num_points vs num_temperatures.
    The first contains the i values while the second contains the q values.'''

    num_points = vna.points
    I = np.zeros((len(temps), len(freqs_ranges)/2, num_points))
    Q = np.zeros((len(temps), len(freqs_ranges)/2, num_points))
    f = np.zeros((len(freqs_ranges)/2, num_points))

    hf = h5py.File('values_different_frequenzy_sweeps', 'w')

    numtemps = len(temps)
    for k in range(numtemps): 
        fridge.set_T(temps[k])
        time.sleep(200)
        ok = fridge.check_stability(temps[k]/10, temps[k])
        if ok == True:      #then we can start to cycle on the different frequency ranges...
            
            for m in range(4):  
                start_freq = freqs_ranges[m]
                stop_freq = freqs_ranges[m+1]
                vna.set_range_freq(start_freq, stop_freq)
                i, q = vna.get_data(format_data)
                I[k, m, :] = i
                Q[k, m, :] = q
                f[m, :] = vna.freqs          
                #we want to store the data in a highly organize way...
                hfdat = hf.create_group('temp_' + str(temps[k]) + 'K_' + 'Start' + str(start_freq) + '_' + 'Stop' + str(stopfreq) + 'GHz')
                hfdat.create_dataset('I', data = i)
                hfdat.create_dataset('Q', data = q)
                hfdat.create_dataset('freqs', data = f)
            
        elif ok == False:
            print ('I had some trouble with the stability of temperature ' + str(temps[k]))
            vna.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it"],"Temperature not stable","I had some trouble with the stability of temperature " + str(temps[k]) + "Do something plis.")
            k = numtemps + 1         
    
    return f, I, Q


def amp_phase(I, Q):
    '''Outputs two matrices with dimensions num_points vs num_temperatures.
    The first contains the S_21 (??) amplitude values while the second contains the S_21 (??) phase values'''
    #a is the S_21 amplitude vector and p is the S_21 phases vector
    #A is the S_21 amplitude matrix and P is the S_21 phases matrix

    num_points = len(I[0]) # number of points i.e. usually 1601
    num_temps = len(I) # number of various temperatures

    A = np.zeros(num_temps, num_points)
    P = np.zeros(num_temps, num_points)
    a = np.zeros(num_points)
    p = np.zeros(num_points)

    for j in range(num_temps):
        for k in range(num_points):
            a[k] = np.sqrt(I[j,k]**2 + Q[j,k]**2)
            p[k] = np.arctan(Q[j,k]/I[j,k])
        A[j] = a
        P[j] = p

    return A, P


class FridgeHandler:
    def __init__(self):
        self.inst = pyvisa.ResourceManager().open_resource('ASRL1::INSTR')
        print('Fridgeboy object created correctly!\n')
  
    def execute(self, cmd):
        self.inst.write('$'+ str(cmd))

    def read(self, cmd):                #It may happen that the read command returns strange things with ?s and Es. In that case you can't trust the result
        out = '?'
        while ('?' in out[0]) or ('E' in out[0]) or ('A' in out[0]):
            out = self.inst.query_ascii_values(str(cmd), converter='s')
            #print(out)       
        out = str.rstrip(out[0])
        return out

    def get_sensor(self, cmd = 3):
        '''Measure temperature or pressure of a sensor of the system. Default: MC temperature.'''                           
        k = self.read('R' + str(cmd))
        k = k.replace("R", "")
        k = k.replace("+", "")
        k = float(k)
        return k       

    def scan_T(self, cmd, interval, time):      # cmd -> command that specifies which temperature,
                                                # interval -> time step to perform control
                                                # time -> total time of the scansion
        '''Temperature scansion that prints the values every "interval" seconds for a "time" time'''
        N = int(time/interval)
        Temps = np.zeros(N)
        for i in range(N):
            out = self.inst.query_ascii_values(cmd, converter='s')
            out = str.rstrip(out[0])
            time.sleep(interval)
            out = (out.split('+'))[1]           # split the string where '+' is and gives back only the second part (1)
            Temps[i] = float(out)
            print('Temperature at step ' + i + ' is ' + out)
        return Temps

    def state(self):
        out = self.inst.query_ascii_values('X', converter='s')
        out = str.rstrip(out[0])
        print(out)
    
    def set_T(self, T):
        '''Set temperature of the mixing chamber to arbitrary value in 0.1 mK. 
        Be careful! The value of temp has to be specified with 5 figures!
        Range is the command name for the power range (E1, E2 ...)'''
        
        cmd = 'E'
        if T <= 50:
            cmd += '1'
        elif T <= 90:
            cmd += '2'
        elif T <= 140:
            cmd += '3'
        elif T <= 400:
            cmd += '4'
        else:
            cmd += '5'

        self.execute(cmd)
        self.execute('A2')
        self.execute('T' + str(10*int(T)))

    def send_email_yahoo(self, fromMy , to, subj, message_text ):         #Be careful, the 'to' variable has to be an array. Put brackets even if it's a single address.
        date = 1/1/2000
        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( fromMy, to, subj, date, message_text )
 
        server = smtplib.SMTP("smtp.mail.yahoo.com",587)
        server.starttls()
        password = str('########')  
        server.login(fromMy,password)
        for account in to:
            server.sendmail(fromMy, account, msg)
        server.quit()    
        print ('ok the emails have been sent ')

    def check_p(self):
        out = self.get_sensor(14) < 100000 and self.get_sensor(15) < 1000000  #!!!!!!!!!!! check the pressure values
        if (not out):
            print("High pressure! O_O' ")
            self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
            "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"High pressure!","la pressione è alta")
        return out  

#Possiamo provare ad implementare un tempo dopo il quale, se la temperatura non è stabile, usciamo dal ciclo?    
    def check_stability(self, T, error, sleeptime = 5, pause = 10):     # T --> desired temperature
                                                                                        # error --> uncertainty allowed on the temperature
                                                                                        # interval --> minimum time of stability required. Defaults to 1 minute and half                                                             # sleeptime --> time interval between each check. Defaults to 5 seconds
        counter = 0
        countermax = 10
        out = False
        while (counter < countermax): 
            if self.get_sensor(21) < 5:
                self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"Low pressure!","la pressione P2 è scesa sotto a 5 mbar") 
                counter = countermax + 1                                                             
            if self.get_sensor(2) > 22000:
                self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"High temperature!","la temperatura della 1K Pot ha superato i 2.2 K")
                counter = countermax + 1
            if (T-error < self.get_sensor() and self.get_sensor() < T + error): # check if values are ok. change get_sensor parameters (actually remove them -> they'll default to mixing chamber) !!!!!!!!
                counter = 0
                print('I found a temperature value out of range. I am going to sleep for ' + str(pause) + ' seconds')
                time.sleep(pause) #sleeps for 10 seconds default minutes if T not stable         
            else:
                counter += 1
                time.sleep(sleeptime) #5 sec of sleep between each T check
        if counter == countermax:
            print("Temperature is stable and fridgeboy is ready!")
            out = True
        return out

# Class for the communication with VNA

class VNAHandler:
    def __init__(self, num_points = 1601):
        self.inst = pyvisa.ResourceManager().open_resource('GPIB0::16::INSTR')
        self.inst.write('FORM2;')
        self.inst.write('CHAN1')
        self.inst.write('S21;')
        self.inst.write('POIN '+ str(num_points)+';')        #set number of points
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        self.points = num_points

        self.freqs = np.zeros(num_points)


        print('VNA object created correctly!\n')
        print('Default number of points for a sweep: ' + str(self.points))

    def set_range_freq(self, start_f, stop_f):
        ''''Set the range of frequencies for the next scan from start_f to stop_f'''
        self.inst.write('LINFREQ;')
        self.inst.write('STAR '+str(start_f)+' GHZ;')       #set start frequency
        self.inst.write('STOP '+str(stop_f)+' GHZ;')        #set stop frequency
        self.inst.write('CONT;')
        self.freqs = np.linspace(start_f, stop_f, self.points)

    def beep(self):
            ''' Emit an interesting sound'''
            self.inst.write('EMIB')
            
    def set_format(self, format):
        ''' Set the format for the displayed data'''
        if format == 'polar':
            write_string = 'POLA;'
        elif format == 'log magnitude':
            write_string = 'LOGM;'
        elif format == 'phase':
            write_string = 'PHAS;'
        elif format == 'delay':
            write_string = 'DELA;'
        elif format == 'smith chart':
            write_string = 'SMIC;'
        elif format == 'linear magnitude':
            write_string = 'LINM;'
        elif format == 'standing wave ratio':
            write_string = 'SWR;'
        elif format == 'real':
            write_string = 'REAL;'
        elif format == 'imaginary':
            write_string = 'IMAG;'

        self.inst.write(write_string)

    def output_data_format(self, format):
        if format == 'raw data array 1':
            msg = 'OUTPRAW1;'
        elif format == 'raw data array 2':
            msg = 'OUTPRAW2;'
        elif format == 'raw data array 3':
            msg = 'OUTPRAW3;'
        elif format == 'raw data array 4':
            msg = 'OUTPRAW4;'
        elif format == 'error-corrected data':
            msg = 'OUTPDATA;'
        elif format == 'error-corrected trace memory':
            msg = 'OUTPMEMO;'
        elif format == 'formatted data':
            msg = 'DISPDATA;OUTPFORM'
        elif format == 'formatted memory':
            msg = 'DISPMEMO;OUTPFORM'
        elif format == 'formatted data/memory':
            msg = 'DISPDDM;OUTPFORM'
        elif format == 'formatted data-memory':
            msg = 'DISPDMM;OUTPFORM'
        
        self.inst.write(msg)  

    def get_data(self, format_data, format_out = 'formatted data'):
        '''Get data of a certain type'''

        self.set_format(format_data)
        self.output_data_format(format_out)
        
        num_bytes = 8*int(int(float(self.points)))+4
        #time.sleep(2)
        raw_bytes = self.inst.read_bytes(num_bytes)

        trimmed_bytes = raw_bytes[4:]
        tipo = '>' + str(2*int(float(self.points))) + 'f'
        x = struct.unpack(tipo, trimmed_bytes)

        amp_q = list(x)
        amp_i = amp_q.copy()

        del amp_i[1::2]
        del amp_q[0::2]

        i = np.array(amp_i)
        q = np.array(amp_q)

        #plt.plot(amp_i, amp_q)

        return i, q

class FastGiorgio:
    def __init__(self):
        self.inst = pyvisa.ResourceManager().open_resource('ASRL25::INSTR')
        print('Giorgio by Moroder listened correctly!\n')

    def hex_freq_converter(self, num):
        '''num is a frequency in MHz'''
        
        freq_mhz = num*10**9
        freq_hex = hex(freq_mhz)
        freq_hex = freq_hex.replace("0x","")
        if len(freq_hex) == 10:
            freq_hex = "00" + freq_hex
        elif len(freq_hex) == 11:
            freq_hex = "1" + freq_hex

        return "0C" + freq_hex.upper()

    def freq_sweep(self, star_freq, end_freq, num_points = 1601, power = 15, dtime = 200):
        '''please give the frequency in MHz'''

        #il primo comando della stringa è un 17 se voglio un Fast sweep

        star_freq_hex = self.hex_freq_converter(star_freq)  
        end_freq_hex = self.hex_freq_converter(end_freq)

        #num_freq = np.linspace(star_freq, end_freq, num_points)

        num_points_hex = hex(num_points).replace("0x","")
        power_hex = "00" + hex(power).replace("0x","")      
        dtime_hex = "00" + hex(dtime).replace("0x","")  

        num_run = "0001" #only 1 run

        trigger_direction = "04" # No trigger and sweep direction up

        header = "17" #for fast sweep mode

        cmd = header + star_freq_hex + end_freq_hex + num_points_hex.upper() + power_hex.upper() + dtime_hex.upper() + num_run + trigger_direction
        self.inst.write(cmd)
        
    def single_freq(self, freq): # insert frequency in  MHz
        self.inst.write("FREQ " + str(freq) + "MHz")

    def power_on(self):
        self.inst.write("OUTP:STAT ON")

    def power_off(self):
        self.inst.write("OUTP:STAT OFF")

    def ext_ref(self):
        self.inst.write("ROSC:SOUR EXT")

    def int_ref(self):
        self.inst.write("ROSC:SOUR INT")



def single_acquisition(time, n_samp):  # Singola acquisizione di n_samp valori in time tempo. Fatto con un solo canale
                                                                                             
    t = np.linspace(0, time, n_samp)
    samp_rate = float(n_samp / time)
    taskHandle = TaskHandle()
    read = int32()
    data = np.zeros((n_samp,), dtype=np.float64)
    N_avg = 10
    
    data_set = np.zeros(shape = (N_avg, n_samp))
    for i in range(N_avg):
        try:
            # DAQmx Configure Code
            DAQmxCreateTask("",byref(taskHandle))
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCfgSampClkTiming(taskHandle,b"",samp_rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,n_samp)

            # DAQmx Start Code
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, n_samp, 10.0,DAQmx_Val_GroupByChannel,data,n_samp,byref(read), None)
            if i%10==0:
                print(i)
                print("Acquired %d points"%read.value)
    
        except DAQError as err:
            print("DAQmx Error: %s"%err)
        finally:
            if taskHandle:
                # DAQmx Stop Code
                DAQmxStopTask(taskHandle)
                DAQmxClearTask(taskHandle)

        data_set[i] = data

    mean_data = data_set.mean(axis = 0)

    plt.plot(t, mean_data) 
    return t, mean_data 


def multi_channel_acq(time, n_samp): #Acquisizione su più canali

    t = np.linspace(0, time, n_samp)
    samp_rate = float(n_samp / time)
    taskHandle = TaskHandle()
    read = int32()
    data = np.zeros((n_samp*4,), dtype=np.float64)
    N_avg = 10
    
    data_set = np.zeros(shape = (N_avg, n_samp*4))
    for i in range(N_avg):
        try:
            # DAQmx Configure Code
            DAQmxCreateTask("",byref(taskHandle))
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai1","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai2","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai3","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCfgSampClkTiming(taskHandle,b"",samp_rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,n_samp)

            # DAQmx Start Code
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, n_samp, 10.0, DAQmx_Val_GroupByChannel, data, n_samp*4, byref(read), None)
            if i%10==0:
                print(i)
                print("Acquired %d points"%read.value)
            
            #plt.plot(t, data[2000:4000])
        
        except DAQError as err:
            print("DAQmx Error: %s"%err)
        
        finally:
            if taskHandle:
                # DAQmx Stop Code
                DAQmxStopTask(taskHandle)
                DAQmxClearTask(taskHandle)
        data_set[i] = data

    mean_data = data_set.mean(axis = 0)

    #plt.plot(t, mean_data) 
    return t, mean_data 
        

#def avg_acquisition():     #Metodo che useremo quando dovremo scansionare la risonanza ma con i sintetizzatori. Devi trovare modo per acquisire due canali contemporaneamente.
                            #Per la misura di fisica vera sarà ancora piu sbatti perchè dovrai acquisire 4 canali e impostare un sistema di trigger


