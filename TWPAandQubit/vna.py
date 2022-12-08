import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class ManageInstrument:
    """
    This class allows creating an Object with:
    - Just one field "instr" that allows sending queries to the instrument: instr.query("<query in SCPI language>")
    - A bunch of methods that make simple sending queries to the instrument, without explicitly writing the SCPI commands 
    - A method "single_scan(...)" that makes the instrument measure the S21 spectrum (see more in the method definition)
    """
    # HOW THE INSTRUMENT WORKS (operatively):
    # In [Continuos scan] mode, the instrument makes consecutive scans of the displayed frequency interval.
    # At each scan, it measures S21 for each frequency in the interval. The results go in the memory of
    # the instrument, where it stores the LAST "navgs" measures. Once it performs a new scan, the oldest
    # measurement in the memory is replaced by the new scan measurement.
    # The value displayed on the screen its an average of all the "navgs" measurements stored in the memory.  
    #
    # HOW WE WANT TO USE IT:
    # We want to use it in [Single scan] mode. First we clear the memory of the instrument, then we perform
    # "navgs" scans that fill the memory of the instrument and at last we read the values displayed on the screen,
    # which are an average of the "navgs" measurements performed.
    # 
    # Before performing the task above, we query the instrument setting the displayed frequency interval, the number
    # of equidistant frequency to sample and "navgs" (the number of scans performed).
    # 
    # The "singleScan(...)" method makes the instrument do it.

    def __init__(self, ip):
        # Open connection to instrument
        rm = visa.ResourceManager()
        self.instr = rm.open_resource("TCPIP0::"+str(ip)+"::inst0::INSTR")

    def close(self, ip):
        # Close connection to instrument
        self.instr.close()
    
    def get_id(self):
        #get the name of the istrument  
        self.instr.query("*IDN?")

    def reset(self):
        #Reset any query
        self.instr.query('*RST')
    
    def single_scan(self,fmin,fmax,powerdBm,npoints,navgs): 
        """
        Usage: <da scrivere>
        """

        #Set the the desired frequency range to display on the screen (measurements are performed on the displayed range)
        self.set_range(fmin,fmax)
        
        #Set desired output power
        self.set_power(powerdBm)
        
        #Set number of sampled frequencies in the displayed frequency range (number of sweep points)
        self.set_sweep_points(npoints)
        
        #Set number of averages (number of sweeps done in a single scan, it is the number of times
        #the value at a frequency is measured and then those navgs values are averaged and then displayed)
        self.set_average(navgs)
        
        #Autoscale y axis displayed range
        self.autoscale()

        #With the instructions above we prepared the display. Now we call a function that makes
        #the "navgs" sweeps, so at the end of the function we'll see the averaged measurements on the screen.
        self.make_sweeps()
        
        #Puts the displayed data into arrays
        freq, I, Q = self.readIQ()

        #Now we got the desired values, we set the display of the instrument in a way that is usefull
        #to see real time changes on the trasmission line
        self.instr.query('INIT:CONT 1;*OPC?') #Set continuos sweep
        self.set_average(1)

        
        return freq,I,Q

    def make_sweeps(self):
        #Clear the memory of the instrument (past sweeps measurements)
        self.instr.query('AVER:CLE;*OPC?')
        
        #Set to single sweep (we want to do exactly "navgs" sweeps)
        self.instr.query('INIT:CONT 0;*OPC?')
        
        #Get "navgs", that is the number of sweep we want to make ("navgs" is set by the user in "singleScan(...)")
        #NOTA: We want "navgs" be a variable in the memory of the instrument (that in the instrument its called "AVER"),
        #because the instrument stores in its memory the measurements of the LAST "AVER" sweeps. So "navgs" cannot be
        #a field of this class, but shall be a variable stored in the instrument memory. So to set or read that,
        #we have to query the instrument.
        navgs = int(self.instr.query('AVER:COUN?'))

        #Makes "navgs" sweeps, by querying "navgs" times the instrument to perform a single scan
        for i in np.arange(0,navgs):
            #Perform a single sweep then wait (*OPC?)
            self.instr.query('INIT:IMM;*OPC?')
        
    def readIQ(self):
        #Read I (real part of S21)
        self.instr.query('CALC:FORMat REAL;*OPC?')  #Display real part, in Linear scale
        self.autoscale()
        freq,I=self.read_data()  #Effectively reads what is displayed on the screen

        #Read Q (imaginary part of S21)
        self.instr.query('CALC:FORMat IMAG;*OPC?')  #Display imaginary part, in Linear scale    
        self.autoscale()
        freq,Q=self.read_data() #Effectively reads what is displayed on the screen

        #Displays S21dB
        self.instr.query('CALC:FORMat MLOG;*OPC?')  #Display modulus (S21), in dB   
        self.autoscale()

        return freq, I, Q

    def read_data(self):
        """
        Effectively reads what is displayed on the screen. Returns 2 arrays containing
        the X and Y coordinates of the points of the graph displayed on the screen.
        """

        #Read Y values
        data = self.instr.query('CALC:DATA:FDAT?')
        #The result of the query above is a STRING containing values separated by "," (comma)
        #So we have to SPLIT the string into an array of values
        data.Split(",")
        
        #Read X values
        freq = self.instr.query('FREQuency:DATA?')
        freq.Split(",")      

        #Wait
        self.instr.query('*OPC?')

        return freq, data

    def set_mode(self,mode):
        # Select mode of instrument (NA or SA)
        if str(mode) == "NA":
            self.instr.query('INST:SEL "NA";*OPC?')
        elif str(mode) == "SA":
            self.instr.query('INST:SEL "SA";*OPC?')
        else:
            print("MODALITA NON CONSENTITA")

    def autoscale(self):
        #Make the trace 1 active
        trace=1
        self.instr.query('CALC:PAR'+ str(trace)+':SEL;*OPC?')
        #Autoscale the y axes
        self.instr.query('DISP:WIND:TRAC'+str(trace)+':Y:AUTO;*OPC?')

    def set_sweep_points(self,npoints):
        #Set the number of sample points in the displayed(!!) frequency range 
        npoints=round(abs(npoints))
        if (npoints > 10001):
            npoints = 10001
        self.instr.query('SWE:POIN '+str(npoints)+';*OPC?')    

    def set_power(self,powerdBm):
        #Set the output power of the segnal 
        if(powerdBm>3):
            powerdBm=3
        if(powerdBm<-45):
            powerdBm=-45
        self.instr.query('SOUR:POW '+str(round(powerdBm,1))+';*OPC?') 

    def set_range(self,min,max):
        #Set the min of the freq range
        self.instr.query('FREQ:START '+str(min)+';*OPC?');
        #Set the max of the freq range
        self.instr.query('FREQ:STOP '+str(max)+';*OPC?');

    #if you set a high number you have to wait till the instrument execute at least navgs measure
    def set_average(self,navgs):
        #Set the number of average for every frequency
        navgs=round(abs(navgs))
        if(navgs>100):
            navgs=100
        self.instr.query('AVER:COUN '+str(navgs)+';*OPC?')

    def get_average(self):
        #Get the number of average 
        navgs=self.instr.query('AVER:COUN?')
        return navgs     

    def set_log_scale(self):

        self.instr.query('CALC:FORMat MLOG;*OPC?')

    def set_lin_scale(self):
        self.instr.query('CALC:FORMat MLIN;*OPC?')

def IQ_to_S21(self,I,Q):
    """
    Calculates S21 in dB, from its real I and imaginary Q parts
    """
    S21dB = 20*np.log10(np.sqrt(np.multiply(I,I)+np.multiply(Q,Q)))
    return S21dB

    