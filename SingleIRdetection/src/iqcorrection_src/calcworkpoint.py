import numpy as np
from scipy import stats
from matplotlib import pyplot as plt

import globvar
from loadiq import LoadIQ
from evaluatepos import EvaluatePos
from readdata import ReadData

# Calcolate working point frequency and eventually correct it.
# 2 possible modes:
# 
# 0 calculate frequency and shift the pulse on the closest point of the circle
# 2 manual selection of the working point

def CalcWorkPoint(spectra_file_name, npoints, ncol, coli, colq, iqfileheader, ifplot):
    
    adcconv = globvar.adcconv
    checkpath = globvar.checkpath
    dataformat = globvar.dataformat
    recordlength = globvar.recordlength

    npoints = int(npoints)
    ncol = int(ncol)
    bb = int(round(npoints/5))
    posbuff = list()

    #Load I and Q from the data file. Not any IQ dataset: we load IQ data relative to a frequency sweep witrh the cryostat cold and connected!
    [f, idata, qdata] = LoadIQ(iqfileheader + '_')

    for j in range(50):
        #Load I and Q from the spectra file, aka the file containing the pulse data
        [idata_spectra, qdata_spectra] = ReadData(spectra_file_name, coli, colq, npoints*j, npoints*(j + 1))

        if len(idata_spectra) == len(qdata_spectra) and len(idata_spectra) == npoints:
        #Correct for the mixer - first remove the DC offsets.  We could either use
        #the offset IQ scan or use the offsets found from the IQ calibration data
        #5/2^15 is the ADC to volts scaling

            if (dataformat == 'int16'):
                signali = adcconv*idata_spectra/(2**15)
                signalq = adcconv*qdata_spectra/(2**15)
            else:
                signali = idata_spectra
                signalq = qdata_spectra
            
            avg = stats.trim_mean(idata_spectra, 0.25)
            #Detect baseline by using max trigger
            minf1 = np.max(np.abs(idata_spectra - avg))
            posf1 = np.argmax(np.abs(idata_spectra - avg))

            if (posf1/npoints > 0.25):
                noisei = signali[0: bb - 1]
                noiseq = signalq[0: bb - 1]
            else:
                noisei = signali[npoints - bb - 1: npoints]
                noiseq = signalq[npoints - bb - 1: npoints]
                
            b = np.mean(noisei)
            c = np.mean(noiseq)

            #min = np.min((idata-b)**2 + (qdata-c)**2)
            pos = np.argmin((idata-b)**2 + (qdata-c)**2)
            posbuff.append(pos)

            if coli == 0:
                nch = 1
            else:
                nch = 2

            if ifplot == 1 and j%9 == 0:
                plt.plot(signali, signalq, 'g', linewidth = 1.5, label = 'Spectra')
                plt.plot(idata, qdata, 'r', linewidth = 1.5, label = 'IQ Data')
                plt.plot(idata[pos], qdata[pos], 'b', label = 'I,Q[pos]', marker = '+')
                plt.title(" - CalcWorkPoint() -> " + str(j) + '-th plot for channel ' + str(nch))
                plt.legend(loc = "upper left")
                plt.show()
                plt.close()
                
    posbuff = np.array(posbuff)
    pos = EvaluatePos(posbuff, 20)
    fmeas = f[pos]

    return [pos, fmeas]



        