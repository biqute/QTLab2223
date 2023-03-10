import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class ManageSIM:
    def __init__(self, resource):
        """Open connection to instrument"""
        
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource)
        self.instr.query("*IDN ?\n")
        self.instr.write('CONN '+str(4)+', "main_esc"')    #SIM928 it's installed on the 4° binary
        
        pass

    def set_voltage(self, value):

        cmd = "VOLT "+str(value)        #Set voltage, "value" is in Volt
        self.instr.write(cmd) 

    def set_output(self,value):          #takes a value: 0 or 1
        
        if(value==0):                   #tunr off the output
         self.instr.write("OPOF")  
        if(value==1):                   #turn on the output
         self.instr.query("OPON")


    def get_output(self):
        return self.instr.query("EXON?")

    
    def close(self):
        """Close connection to instrument"""
        self.instr.close()

        