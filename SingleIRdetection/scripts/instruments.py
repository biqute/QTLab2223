# Library for communication with the instruments

import pyvisa
import numpy as np
import time
import smtplib, ssl
from matplotlib import pyplot as plt
import struct


#with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#server.login("mail@gmail.com", password)

def measure(fridge, vna, temps, format_data):
    '''Outputs two matrices with dimensions num_points (1601) vs num_temperatures.
    The first contains the I values while the second contains the Q values.'''
    
    num_points = vna.points
    I = np.zeros((len(temps), num_points ))
    Q = np.zeros((len(temps), num_points))
    j = 0

    for t in temps:
        fridge.set_T(t)
        # Maybe we need to add a sleep? How long?
        ok = fridge.check_stability(t/10, t)
        if ok == True:
            i, q = vna.get_data(format_data)
            I[j] = i
            Q[j] = q
            j += 1
        else:
            print ('I had some trouble with the stability of temperature ' + str(t))
            break           #Fix this. you should find soething like an error return
        f = vna.freqs
        
    return I, Q, f

def amp_phase(I, Q):
    '''Outputs two matrices with dimensions num_points vs num_temperatures.
    The first contains the S_21 amplitude values while the second contains the S_21 phase values.'''
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

# Class to communicate with the Gas Handler
class FridgeHandler:
    def __init__(self):
        self.inst = pyvisa.ResourceManager().open_resource('ASRL1::INSTR')
        print('Fridgeboy object created correctly!\n')
  
    def execute(self, cmd):
        '''Send a command to the instrument. 
        This method automatically adds a '$' to make the string understandable for the instruments.'''
        self.inst.write('$'+ str(cmd))

    def read(self, cmd):
        '''Read a value from the instrument. 
        This method also checks if the output has a problem and if this is the case sends again the command.'''
        out = '?'
        print(out)
        while ('?' in out[0]) or ('E' in out[0]):
            out = self.inst.query_ascii_values(str(cmd), converter='s')
            print(out)       
        out = str.rstrip(out[0])
        return out

    def get_sensor(self, cmd = 3):
        '''Measure temperature or pressure of a sensor of the system. 
        Default: MC temperature (R3).'''                           
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
        '''Method that return the state of the instrument, i.e. the command 'X''''
        out = self.inst.query_ascii_values('X', converter='s')
        out = str.rstrip(out[0])
        print(out)
    
    def set_T(self, T):
        '''Set temperature of the mixing chamber to arbitrary value in 0.1 mK. 
        Be careful! The value of temp has to be specified with 5 figures!
        Range is the command name for the power range (E1, E2 ...)'''
        
        cmd = 'E'
        if T <= 35:
            cmd += '1'
        elif T <= 55:
            cmd += '2'
        elif T <= 140:
            cmd += '3'
        elif T <= 400:
            cmd += '4'
        else:
            cmd += '5'

        self.execute(cmd)
        self.execute('A2')
        self.execute('T' + str(10*T))

    def send_email_yahoo(self, fromMy , to, subj, message_text ):         #Be careful, the 'to' variable has to be an array. Put brackets even if it's a single address.
        '''Method that send and e-mail.'''
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
        '''Checks the pressure '''
        out = self.get_sensor(14) < 100000 and self.get_sensor(15) < 1000000  #!!!!!!!!!!! check the pressure values
        if (not out):
            print("High pressure! O_O' ")
            self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
            "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"High pressure!","la pressione è alta")
        return out  

#Possiamo provare ad implementare un tempo dopo il quale, se la temperatura non è stabile, usciamo dal ciclo?    
    def check_stability(self, T, error, interval = 90, sleeptime = 5, pause = 300):    # T --> desired temperature
                                                                            # error --> uncertainty allowed on the temperature
                                                                            # interval --> minimum time of stability required. Defaults to 1 minute and half
        t0 = time.time()                                                                    # sleeptime --> time interval between each check. Defaults to 5 seconds
        counter = 0
        countermax = int(interval/sleeptime)
        while (counter < countermax) and (time.time() - t0 < 1801): 
            if self.get_sensor(21) < 5:
                self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"Low pressure!","la pressione P2 è scesa sotto a 5") 
                counter = countermax + 1                                                             
            if self.get_sensor(2) > 22000:
                self.send_email_yahoo("leomaria2906@yahoo.com",["l.mariani48@campus.unimib.it","a.angeloni3@campus.unimib.it",
                "m.faggionato1@campus.unimib.it","marco.faverzani@unimib.it"],"High temperature!","la temperatura della 1 K Pot ha superato i 2.2K")
                counter = countermax + 1
            if self.check_p() == False or not (T-error < self.get_sensor(2) and self.get_sensor(2) < T + error): # check if values are ok
                # change get_sensor parameters (actually remove them -> they'll default to mixing chamber) !!!!!!!!
                counter = 0
                print('I found a temperature value out of range. I am going to sleep for ' + str(pause) + ' seconds')
                time.sleep(pause) #sleeps for 6 default minutes if T not stable         
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

        plt.plot(amp_i, amp_q)

        return amp_i, amp_q

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

        star_freq_hex = self.hex_freq_converter(star_freq)  
        end_freq_hex = self.hex_freq_converter(end_freq)

        num_freq = np.linspace(star_freq, end_freq, num_points)

        num_points_hex = hex(num_points).replace("0x","")
        power_hex = "00" + hex(power).replace("0x","")      
        dtime_hex = "00" + hex(dtime).replace("0x","")  
