import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
from RsInstrument import *

class ManageFSV:
    
    def __init__(self, resource):
        """Open connection to instrument"""

        self.instr = RsInstrument(resource)       
        pass

    def close(self):
        """Close connection to instrument"""
        self.instr.close()
    

    def reset(self):
        #self.instr.clear_status() # Seems to do nothing
        self.instr.reset() #SETS CF 15GHz; Span 30GHz
        self.instr.write_str('SYST:DISPlay:UPDATE ON')  # Display update ON
        self.instr.write_str('DISPlay:WINDow:TRACe:Y:SCALe:AUTO ONCE')  # Autoscales Y axis


    def single_scan(self,fmin,fmax,npoints,navgs): 
        """
        Tells the device to perform "navgs" times a scan of the S21 spectrum in the frequency span [fmin,fmax]
        by sampling "npoints" equal spaced frequencies.
        This function returns the values displayed on the device screen (which are an average of the measurements) in 2 arrays:
        "freq": List of the sampled frequencies [Hz];
        "trace": List of sampled power [dBm];
        """

        # SET SINGLE SWEEP MODE - The single sweep mode of this device is non-trivial:
        # When the device is in this mode, if we order to permorm a single sweep, it will not perform
        # just 1 scan, but will perform a number of scans equal to the number of averages we
        # requested to do (After taking thos measurments, the device displays the average of THOSE measurements)
        self.instr.write_str_with_opc('INITiate:CONTinuous OFF')    #Single sweep mode 
        
        # Set the number of consecutive sweeps performed when a single sweep is queryied,
        # that equals the number of averaged measurements
        self.set_average(navgs)
        
        # Set to average mode, which means that the device displays an average of the
        # "navgs" measurements it takes when a single sweep is queryied. If this mode is not
        # set, the device could display the last measurement and not an average.
        self.instr.write_str('DISP:WIND:TRAC:MODE AVER')

        # Set the frequency span and number of sampled frequencies
        self.set_range(fmin, fmax)
        self.set_sweep_points(npoints)
        
        # Query a single sweep, so the device makes "navgs" consecutive sweeps.
        self.instr.write_str('INIT;*WAI')   # Waits until all the sweeps are finished

        # Autoscales Y axis
        self.instr.write_str('DISPlay:WINDow:TRACe:Y:SCALe:AUTO ONCE')  # Setting the center frequency

        # Reads into arrays the results displayed on the device screen
        freq, trace = self.read_data()

        # Set to continuos scan (to make the device useful for non-remote usage)
        self.instr.write_str_with_opc('INITiate:CONTinuous ON')
        
        return freq, trace


    def set_range(self,min,max):
        # Set the max of the freq range
        self.instr.write_str_with_opc('SENS:FREQ:STOP '+str(max)+';*OPC');
        # Set the min of the freq range
        self.instr.write_str_with_opc('SENS:FREQ:START '+str(min)+';*OPC');

    
    def set_sweep_points(self,npoints):
        # Set the number of sample points in the displayed(!!) frequency range 
        npoints=round(abs(npoints))
        if (npoints > 10001):
            npoints = 10001
        self.instr.query_str_with_opc('SWE:POIN '+str(npoints)+';*OPC?')  


    def set_average(self,navgs):
        """
        Number of averaged measurements, whose average is displayed.
        The number of averages equals the number of consecutive sweeps
        performed when a single sweep is queryied.
        """

        self.instr.write_str('SWE:COUN ' + str(navgs))
        # Equivalentl instruction below (average number = sweeps number)
        #self.instr.write_str('SENSe:AVERage:COUNt '+str(navgs))


    def get_average(self):
        self.instr.query_str_list_with_opc('AVER:COUN?')


    def set_RBW(self,value):
        self.instr.write_str('BAND '+str(value)+' Hz')  # Typical 200kHz


    def set_VBW(self,value):
        self.instr.write_str('BAND:VID '+str(value)+'Hz')   # Typical 300kHz


    def set_power_reference_level(self,value):
        self.instr.write_str('DISPlay:WINDow:TRACe:Y:SCALe:RLEVel '+str(value)+'DBM')  # Setting the displayed Y Reference Level [dBm]


    def read_data(self):
        """Returns the displayed spectrum into two separate arrays"""

        # Read Y data
        trace = self.instr.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE1')  # Query ascii array of floats
        # Reconstruct x data (frequency for each point) as it can not be directly read from the instrument
        start_freq = self.instr.query_float('FREQuency:STARt?')
        stop_freq = self.instr.query_float('FREQuency:STOP?')
        freq = np.linspace(start_freq,stop_freq)

        return freq, trace