# Class we use to communicate with the DAQ

import pyvisa
import numpy as np
from matplotlib import pyplot as plt
from PyDAQmx import TaskHandle, byref, int32, DAQmxCreateTask, DAQmxCreateAIVoltageChan, DAQmxCfgSampClkTiming, DAQmxStartTask, DAQmx_Val_Cfg_Default, DAQmx_Val_Rising, DAQmx_Val_Volts, DAQmx_Val_FiniteSamps, DAQmxReadAnalogF64, DAQmx_Val_GroupByChannel, DAQError, DAQmxStopTask, DAQmxClearTask

def single_acquisition(time, n_samp): 
    '''Single acquisition of "n_samp" values during a certain period defined in "time". 
    This method uses a single channel.'''                                                                                  
    t = np.linspace(0, time, n_samp)
    samp_rate = float(n_samp / time)
    taskHandle = TaskHandle() # Creates the task of the instrument
    read = int32()
    data = np.zeros((n_samp,), dtype=np.float64) # line vector with n_sample values of type float64

    N_avg = 10 # Number of dataset acquired to be averaged
    
    data_set = np.zeros(shape = (N_avg, n_samp)) # matrix N_avg lines x n_sample columns
    for i in range(N_avg):
        try:
            # DAQmx Configure Code
            DAQmxCreateTask("",byref(taskHandle))
            DAQmxCreateAIVoltageChan(taskHandle,b"Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
            DAQmxCfgSampClkTiming(taskHandle,b"",samp_rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,n_samp)

            # DAQmx Start Code
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, n_samp, -1, DAQmx_Val_GroupByChannel, data, n_samp, byref(read), None)
            
            print("data acquired for the cycle " + str(i))
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

    #plt.plot(t, mean_data) 
    return t, mean_data, data_set


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
    return t, mean_data, data_set