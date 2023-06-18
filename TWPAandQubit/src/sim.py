import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class ManageSIM:
    def __init__(self, resource):
        """Open connection to instrument"""
        
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource)
        self.instr.timeout = 15e3
        print(self.instr.query("*IDN ?\n"))
        self.instr.write('CONN '+str(4)+', "main_esc"')    #SIM928 it's installed on the 4° binary
        
        pass

    def set_voltage(self, value):
        cmd = "VOLT "+str(round(value,3)) + ";*OPC?\n"        #Set voltage, "value" is in Volt
        return self.instr.query(cmd) 

    def set_output(self,value):          #takes a value: 0 or 1
        if(value==0):                   #tunr off the output
         self.instr.query("OPOF;*OPC?\n")
        if(value==1):                   #turn on the output
         self.instr.query("OPON;*OPC?\n")

        # Check
        return self.get_output()

    def get_output(self):
        temp_out = self.instr.query("EXON?\n")
        temp_vec_out = temp_out.split("\r\n")
        return temp_vec_out[0]

    def get_voltage(self):
        temp_out = self.instr.query("VOLT?\n")
        temp_vec_out = temp_out.split("\r\n")
        return temp_vec_out[0]        

    def reset(self):
        numbits = self.instr.write("*RST\n")
        return numbits

    def close(self):
        """Close connection to instrument"""
        self.instr.close()

        