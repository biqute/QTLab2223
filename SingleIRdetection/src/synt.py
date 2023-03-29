# Class we use to communicate with the synthetizer

import pyvisa
import numpy as np

class FastGiorgio:
    def __init__(self, channel):
        '''channel -> we have two different channels: "??ASRL25::INSTR??" and ""'''
        self.inst = pyvisa.ResourceManager().open_resource(str(channel))
        print('Giorgio by Moroder listened correctly!\n')

    def hex_freq_converter(self, num):
        '''Converts a number in hexadecimal as required by the instrument.        
        "num" is a frequency in MHz'''
        
        freq_mhz = num*10**9
        freq_hex = hex(freq_mhz)
        freq_hex = freq_hex.replace("0x","")
        if len(freq_hex) == 10:
            freq_hex = "00" + freq_hex
        elif len(freq_hex) == 11:
            freq_hex = "1" + freq_hex

        return "0C" + freq_hex.upper()

    def freq_sweep(self, star_freq, end_freq, num_points = 1601, power = 15, dtime = 200):
        '''Does a frequency sweep along 1601 different frequencies.
        star_freq -> starting frequency in MHz
        end_freq -> ending frequency in MHz
        num_points -> number of different frequencies between star_freq and end_freq'''

        # Il primo comando della stringa è un 17 se voglio un Fast sweep

        star_freq_hex = self.hex_freq_converter(star_freq)  
        end_freq_hex = self.hex_freq_converter(end_freq)

        #num_freq = np.linspace(star_freq, end_freq, num_points)

        num_points_hex = hex(num_points).replace("0x","")
        power_hex = "00" + hex(power).replace("0x","")      
        dtime_hex = "00" + hex(dtime).replace("0x","")  

        num_run = "0001" # Only 1 run

        trigger_direction = "04" # No trigger and sweep direction up

        header = "17" # For fast sweep mode

        cmd = header + star_freq_hex + end_freq_hex + num_points_hex.upper() + power_hex.upper() + dtime_hex.upper() + num_run + trigger_direction
        self.inst.write(cmd)
        
    def single_freq(self, freq):
        '''Sends a single frequency. 
        freq -> frequency to be sent in MHz'''
        self.inst.write("FREQ " + str(freq) + "MHz")

    def set_power(self, power):
        """Sets the power of the signal.
        power -> give a value in dBm"""
        self.inst.write("POW " + str(power))

    def power_on(self):
        self.inst.write("OUTP:STAT ON")

    def power_off(self):
        self.inst.write("OUTP:STAT OFF")

    def ext_ref(self):
        self.inst.write("ROSC:SOUR EXT")

    def int_ref(self):
        self.inst.write("ROSC:SOUR INT")