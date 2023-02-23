import h5py
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import fsv
import sma
import vna
import pyvisa
from pathlib import Path
from RsInstrument import *
from datetime import datetime

def manual_S21(instrFSV: fsv.ManageFSV, instrSMA: sma.ManageSMA, powerdBm, fmin, fmax, nfreqs, filename, group, npoints, navgs):
    """
    Calculates S21 spectrum by consecutevly sending with the "sma" a frequency at the desired input power
    throught the line and measuring with the spectrum analyzer ("fsv") the peak heiht in the output signal
    (output power).
    Then it calculates S21dBm = onput_powerdBm - input_powerdBm 

    powerdBm: Input power (power of the generated signal)
    nfreqs: Number of frequencies sent throught the line in the range (fmin, fmax)
    npoints: Number of points of the spectrum analyzer (note: we need just the peak height!)
    navgs: Number of averages of the spectrum analyzer
    """


    # Set the dataset name rule
    full_dataset_name = group + "/" + str(float(fmin/1e9)) + "GHz_" + str(fmax/1e9) + "GHz_" + str(powerdBm) + "dBm"

    # Check if a dataset with the same name already exists
    hf = h5py.File(filename, 'r')
    read_mat = hf.get(full_dataset_name)
    hf.close()
    if read_mat is not None:
        sys.exit("Dataset già esistente!")
    
    # Perform the scan
    freqs = np.linspace(fmin, fmax, nfreqs)
    peaks = np.zeros(len(freqs))

    instrSMA.set_output_on()
    for i in np.arange(nfreqs):
        instrSMA.set_freq(freqs[i])
        time.sleep(0.1)
        fs, output_powerdBm = instrFSV.single_scan(freqs[i]-50e6,freqs[i]+50e6,npoints,navgs)
        peaks[i] = np.max(output_powerdBm)
    instrSMA.set_output_off()

    # Calculate S21dBm
    S21dBm = peaks - powerdBm*np.ones(len(peaks))

    # Save S21dBm data
    hf = h5py.File(filename, 'a')
    mat = [freqs, S21dBm]
    hf.create_dataset(full_dataset_name, data = mat)
    hf.close()

    # Try to read the just written data
    hf = h5py.File(filename, 'r')
    read_mat = hf.get(full_dataset_name)
    read_freqs = read_mat[0]
    read_S21dBm = read_mat[1]
    datasets_list = [key for key in hf.keys()]
    hf.close()

    # Save picture of acquired data
    fig, ax = plt.subplots()
    ax.plot(read_freqs/1e9, read_S21dBm)
    ax.set_xlabel('frequency [GHz]')
    ax.set_ylabel('S21 [dBm]')
    ax.grid(True)
    plt.savefig(full_dataset_name)
    #plt.close(fig)
    plt.show()

    return datasets_list

def acquire_S21(instrVNA: vna.ManageVNA,fmin,fmax,powerdBm,npoints,navgs,filename,group,plot_fig=0):
    """
    Calculates S21 spectrum with VNA

    powerdBm: Input power (power of the generated signal)
    nfreqs: Number of frequencies sent throught the line in the range (fmin, fmax)
    npoints: Number of points of the spectrum analyzer (note: we need just the peak height!)
    navgs: Number of averages of the spectrum analyzer
    """


    # Set the dataset name rule
    full_dataset_name = group + "/" + str(float(fmin/1e9)) + "GHz_" + str(fmax/1e9) + "GHz_" + str(powerdBm) + "dBm"

    # Check if a dataset with the same name already exists
    hf = h5py.File(filename, 'a')
    read_mat = hf.get(full_dataset_name)
    hf.close()
    if read_mat is not None:
        sys.exit("Dataset already exists!")
    
    # Perform the scan
    #freq, I, Q = instrVNA.single_scan(fmin,fmax,powerdBm,npoints,navgs)
    freq, S21 = instrVNA.single_scan(fmin,fmax,powerdBm,npoints,navgs)
    # Here we calculate the matrix element in dB, form its real and imaginary parts
    #S21 = vna.IQ_to_S21(I,Q)

    # Save S21dBm data
    hf = h5py.File(filename, 'a')
    mat = [freq, S21]
    hf.create_dataset(full_dataset_name, data = mat)
    hf.close()

    # Save (backup) data in a "per sè" file
    t = round(time.time())
    temp_filename = "backup/" + full_dataset_name.replace("/"," ") + ".h5"
    hf = h5py.File(temp_filename, 'a')
    mat = [freq, S21]
    hf.create_dataset("time " + str(t), data = mat)
    hf.close()

    # Try to read the just written data
    hf = h5py.File(filename, 'r')
    read_mat = hf.get(full_dataset_name)
    read_freqs = read_mat[0]
    read_S21dBm = read_mat[1]
    hf.close()

    # Save picture of acquired data
    if plot_fig == 1:
        fig, ax = plt.subplots()
        ax.plot(read_freqs/1e9, read_S21dBm)
        ax.set_xlabel('frequency [GHz]')
        ax.set_ylabel('S21 [dBm]')
        ax.grid(True)

        # Figure path
        temp_vec = full_dataset_name.split("/")
        figname = temp_vec[len(temp_vec)-1] + ".png"

        plt.savefig(figname)
        plt.close(fig)
        plt.show()
        plt.clf()
        return fig, ax