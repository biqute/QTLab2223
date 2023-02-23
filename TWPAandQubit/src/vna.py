import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

class ManageVNA:
    """
    This class allows creating an Object with:
    - Just one field "instr" that allows sending queries to the instrument: instr.query("<query in SCPI language>")
    - A bunch of methods that make simple sending queries to the instrument, without explicitly writing the SCPI commands 
    - A method "single_scan(...)" that makes the instrument measure the S21 spectrum (more informations in the method definition)
    """

    def __init__(self, ip, timeout = 5e3, max_npoints = 1e3):
        """Open connection to instrument"""
        rm = visa.ResourceManager()
        self.instr = rm.open_resource("TCPIP0::"+str(ip)+"::inst0::INSTR")
        self.instr.timeout = timeout
        self.max_npoints = max_npoints
        # A single scan w/ more than "max_npoints" pts will be split into many

        pass

    def close(self):
        """Close connection to instrument"""
        self.instr.close()
    
    def get_id(self):
        """Get the name of the istrument"""
        return self.instr.query("*IDN?")

    def reset(self,wait_time = 3):
        """
        Reset any query sent to the instrument
        NOTe: You have to re-select the MODe
              and the Sij scattering channel!!!
        """
        self.instr.write('*RST')
        time.sleep(wait_time)   # Before sending queries, we need to wait a while after resetting
    
    def query_reset(self):
        """
        Reset queries queue
        """
        self.instr.query('*CLS;*OPC?')
    
    def single_scan(self,fmin,fmax,powerdBm,npoints,navgs,print_progress=0): 
        """
        Tells the device to perform "navgs" times a scan of the S21 spectrum in the frequency span [fmin,fmax]
        by sampling "npoints" equal spaced frequencies.
        This function returns the values displayed on the device screen (which are an average of the measurements) in 3 arrays:
        "freq": List of the sampled frequencies;
        "Q": Average of the Real part of the "navgs" measures taken at each frequency in "freq";
        "I": Average of the Imaginary part of the "navgs" measures taken at each frequency in "freq";
        
        Use method IQ_to_S21(Q,I) to compute S21 in dB.
        
        "powerdBm" is the output power of the device in dBm (typical value: -15dBm) 
        """

        # Set the the desired frequency range to display on the screen (measurements are performed on the displayed range)
        self.set_range(fmin,fmax)
            
        # Set desired output power in dBm (typical value = -15dBm)
        self.set_power(powerdBm)
            
        # Set number of sampled frequencies in the displayed frequency range (number of sampled frequencies at each sweep)
        self.set_sweep_points(npoints)
            
        # Set number of averages, that is the number of times the value at a same frequency is measured.
        # For each frequency, those measurements are averaged and then displayed on the screen.
        self.set_average(navgs)
            
        # Autoscale y axis displayed range
        self.autoscale()

        # A single scan w/ npoints > "max_npoints" will be SPLIT in many scans!
        if npoints > self.max_npoints:
            nint = np.ceil(npoints/self.max_npoints)
            new_npoints = round(npoints/nint)
            if print_progress == 1:
                print("MULTISCAN triggered with:\nNumber of divided intervals: ",nint,"; Number of pts per interval: ",new_npoints,"; Total number of pts: ",new_npoints*nint)
            return  self.multi_scan(fmin,fmax,powerdBm,new_npoints,navgs,nint)
        else:
            # With the instructions above we prepared the display. Now we call a function that makes
            # the "navgs" sweeps, so at the end of the function we'll see the averaged measurements on the screen.
            self.make_sweeps()

            
            # Puts the displayed data into arrays.
            # - "freq" is the array of the sampled frequencies
            # - "I" and "Q" are respecively the (averaged) measurements of real(I) and imaginary(Q) parts
            # of the selected matrix element (e.g. S21), corresponding to the frequencies in the "freq" array
            #time.sleep(5)

            #freq, I, Q = self.readIQ()
            freq, S21 = self.read_data()

            # Now we got the desired values, we set the display of the instrument in a way that is usefull
            # to see real time changes on the trasmission line
            
            #self.instr.query('INIT:CONT 1;*OPC?') #Set continuos sweep
            
            #self.set_average(navgs)

            
            #return freq,I,Q
            return freq, S21

    def multi_scan(self,fmin,fmax,powerdBm,npoints,navgs,nint,print_progress=0):
        """
        This function is only called by single_scan(). Its not meant to be called by itself!
        If npoints selected for single scan is too high that makes the VNA time out, then this function is called.

        This function divides [fmin,fmax] into "nint" subintervals and calls "single_scan" for each of them.
        Then it merges the data from the many "single_scan" calls.
        """

        fdist=(fmax-fmin)/nint   # Lenght of each subinterval
        sub_fmin = fmin-fdist    # Initialize the subinterval range
        sub_fmax = fmin

        freq_vec=np.zeros(0)    # Initialize array containing MERGED data
        S21_vec = np.zeros(0)
        #I_vec=np.zeros(0)
        #Q_vec=np.zeros(0)

        for i in np.arange(0,nint):
            sub_fmin=sub_fmin+fdist
            sub_fmax=sub_fmin+fdist
            if print_progress == 1:
                print(sub_fmin," - ",sub_fmax)
            #freq, I, Q = self.single_scan(sub_fmin,sub_fmax,powerdBm,npoints,navgs)
            freq, S21 = self.single_scan(sub_fmin,sub_fmax,powerdBm,npoints,navgs)
            
            freq_vec=np.append(freq_vec,freq[1:len(freq)])
            #I_vec=np.append(I_vec,I[1:len(I)])
            #Q_vec=np.append(Q_vec,Q[1:len(Q)])
            S21_vec = np.append(S21_vec,S21[1:len(S21)])

        freq_vec.flatten()
        #I_vec.flatten()
        #Q_vec.flatten()
        S21_vec.flatten()

        # Now we got the desired values, we set the display of the instrument in a way that is usefull
        # to see real time changes on the trasmission line
        
        self.set_range(fmin,fmax)
        self.instr.query('INIT:CONT 1;*OPC?') #Set continuos sweep

        #return freq_vec,I_vec,Q_vec        
        return freq_vec,S21_vec

    def make_sweeps(self):
        # Clear the memory of the instrument (past sweeps measurements)
        self.instr.query('AVER:CLE;*OPC?')
        
        # Set to single sweep (we want to do exactly "navgs" sweeps)
        self.instr.query('INIT:CONT 0;*OPC?')
        
        # Get "navgs", that is the number of sweep we want to make.
        # We want "navgs" be a variable in the memory of the instrument (that in the instrument its called "AVER"),
        # because the instrument stores in its memory the measurements of the LAST "AVER" sweeps. So "navgs" cannot be
        # a field of this class, but shall be a variable stored in the instrument memory. So to set or read that,
        # we have to query the instrument.
        navgs = int(self.instr.query('AVER:COUN?'))

        # Makes "navgs" sweeps, by querying "navgs" times the instrument to perform a single sweep
        for i in np.arange(0,navgs):
            #print("sweep")
            # Perform a single sweep then wait (*OPC?)
            try:
                self.instr.query('INIT:IMM;*OPC?')
            except:
                print("Single sweep timeout ignored. Remaking it")
                self.query_reset()
                self.set_mode("NA")
                self.set_port("S21")
                time.sleep(1)
                self.instr.query('INIT:IMM;*OPC?')
        
    def readIQ(self):
        # Read I (real part of S21)
        self.instr.query('CALC:FORMat REAL;*OPC?')  #Display real part, in Linear scale
        self.autoscale()
        freq,I=self.read_data()  #Effectively reads what is displayed on the screen

        # Read Q (imaginary part of S21)
        self.instr.query('CALC:FORMat IMAG;*OPC?')  #Display imaginary part, in Linear scale    
        self.autoscale()
        freq,Q=self.read_data() #Effectively reads what is displayed on the screen

        # Displays S21dB
        self.instr.query('CALC:FORMat MLOG;*OPC?')  #Display modulus (S21), in dB   
        self.autoscale()

        return freq, I, Q

    def read_data(self):
        """
        Effectively reads what is displayed on the screen. Returns 2 arrays containing
        the X and Y coordinates of the points of the graph displayed on the screen.
        """

        
        
        # Wait
        #self.instr.query('*OPC?')

        # Read Y values
        ydata = self.instr.query('CALC:DATA:FDAT?')
        #self.instr.query('*OPC?')
        #print("read Y time out error ignored")
        # The result of the query above is a STRING containing values separated by "," (comma),
        # so we have to SPLIT the string into an array of values
        ydata_vec = ydata.split(",")
        ydata_vec[-1] = (ydata_vec[-1].split("\n"))[0]
        Ydata_vec = np.zeros(len(ydata_vec))
        for i in np.arange(0,len(ydata_vec)):
            Ydata_vec[i] = float(ydata_vec[i])

        
        
        # Read X values
        freq = self.instr.query('FREQuency:DATA?')
        #print("Read X time out error ignored")
        freq_vec = freq.split(",")
        freq_vec[-1] = (freq_vec[-1].split("\n"))[0]
        Freq_vec = np.zeros(len(freq_vec))
        for i in np.arange(0,len(freq_vec)):
            Freq_vec[i] = float(freq_vec[i])



        return Freq_vec, Ydata_vec

    def set_mode(self,mode):
        # Select mode of instrument (NA or SA)
        if str(mode) == "NA":
            self.instr.query('INST:SEL "NA";*OPC?')
        elif str(mode) == "SA":
            self.instr.query('INST:SEL "SA";*OPC?')
        else:
            print("Invalid mode ",str(mode))

    def set_port(self,port):
        # Select the scattering port Sij
        avaible_ports = ["S11","S12","S21","S22"]
        if port in avaible_ports:
            self.instr.query("CALC:PAR:DEF " + port + ";*OPC?")
        else:
            print("Invalid port ",str(port))
    
    def autoscale(self):
        # Make the trace 1 active
        trace=1
        self.instr.query('CALC:PAR'+ str(trace)+':SEL;*OPC?')
        # Autoscale the y axes
        self.instr.query('DISP:WIND:TRAC'+str(trace)+':Y:AUTO;*OPC?')

    def set_sweep_points(self,npoints):
        # Set the number of sample points in the displayed(!!) frequency range 
        npoints=round(abs(npoints))
        if (npoints > 10001):
            npoints = 10001
        self.instr.query('SWE:POIN '+str(npoints)+';*OPC?')    

    def set_IFBW(self,ifbw):
        # Set the resolution bandwidth (IF bandwith)
        self.instr.query('BWID ' + str(ifbw) + ';*OPC?')

    def set_power(self,powerdBm):
        # Set the output power of the segnal 
        if(powerdBm>3):
            powerdBm=3
        if(powerdBm<-45):
            powerdBm=-45
        self.instr.query('SOUR:POW '+str(round(powerdBm,1))+';*OPC?') 

    def set_range(self,min,max):
        # Set the min of the freq range
        self.instr.query('FREQ:START '+str(min)+';*OPC?');
        # Set the max of the freq range
        self.instr.query('FREQ:STOP '+str(max)+';*OPC?');

    # WARNING: if you set a high number for "navgs" you have to wait till the instrument execute at least navgs measure
    def set_average(self,navgs):
        # Set the number of average for every frequency
        navgs=round(abs(navgs))
        if(navgs>100):
            navgs=100
        self.instr.query('AVER:COUN '+str(navgs)+';*OPC?')

    def get_average(self):
        # Get the number of average 
        navgs=self.instr.query('AVER:COUN?')
        return navgs     

    def set_log_scale(self):
        self.instr.query('CALC:FORMat MLOG;*OPC?')

    def set_lin_scale(self):
        self.instr.query('CALC:FORMat MLIN;*OPC?')

def IQ_to_S21(I,Q):
    """
    Calculates S21 in dB, from its real I and imaginary Q parts
    """
    S21dB = 20*np.log10(np.sqrt(np.multiply(I,I)+np.multiply(Q,Q)))
    return S21dB

    
