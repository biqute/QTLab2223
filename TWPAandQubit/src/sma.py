import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
from RsInstrument import *

class ManageSMA:
    
    def __init__(self, resource):
        """Open connection to instrument"""

        self.instr = RsInstrument(resource)
        self.max_amplitude = -30    # [dBm] Max amplitude permitted to the user
        
        pass

    def close(self):
        """Close connection to instrument"""

        # Turn OFF the OUTPUT
        self.instr.write_str(':OUTPut1 OFF') 
        self.instr.close()
        

    def set_freq(self, freq):
        # Set the frequency of the output signal [Hz]
        self.instr.write_str('SOURce1:FREQuency:CW '+str(freq)) # e.g. 12500000000[Hz]
        # Turn ON the OUTPUT
        self.instr.write_str(':OUTPut1 ON')   
        
    def set_amplitude(self, amplitude):
        # Set the amplitude of the output signal [dBm]
        if amplitude <= self.max_amplitude:
            self.instr.write_str('SOURce1:POWer:LEVel:IMMediate:AMPLitude '+str(amplitude)) # e.g. -40[dBm]
        else:
            print("Set an amplitude < "+str(self.max_amplitude)+"dBm !")
    
    def set_output_off(self):
        self.instr.write_str(':OUTPut1 OFF') 