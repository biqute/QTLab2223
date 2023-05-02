import os
import numpy as np
from scipy import stats

import globvar
from loadiq import LoadIQ
from evaluatepos import EvaluatePos
from mathfunctions import MinColumnWise, MaxColumnWise


def CalcWorkPoint(file_name, npoints, ncol, coli, colq, iqfileheader, mode):
    # Calcolate working point frequency and eventually correct it.
    # 2 possible modes:
    # 
    # 0 calculate frequency and shift the pulse on the closest point of the circle
    # 2 manual selection of the working point

    adcconv = globvar.adcconv
    checkpath = globvar.checkpath
    dataformat = globvar.dataformat

    #print('adcconv = ' + str(adcconv))

    npoints = int(npoints)
    ncol = int(ncol)

    if (mode == 0 or mode == 1):
        fid = open(file_name)
        bb = np.int32(round(npoints/5))
        [f, idata, qdata] = LoadIQ(iqfileheader + '_')
        posbuff = []

        data = np.array(np.fromfile(fid, dtype = '>i2'))
        data = data.reshape([ncol, npoints])

        #for jj in range(200):  #(?)

        #We retrieve data from "filename" and traspose by making it such that we have "npoints" columns
        #and 2*"nchan" rows. If in data we had a column of i, a column of q and so on,
        #now we have a row of i, a row of q and so on 

        #print(data.shape[1])

        if np.shape(data)[1] == npoints:

            #Correct for the mixer - first remove the DC offsets.  We could either use
            #the offset IQ scan or use the offsets found from the IQ calibration data
            #5/2^15 is the ADC to volts scaling

            if (dataformat == 'int16'):
                idata1 = data[coli, :]
                signali = adcconv*(np.ravel(idata1.T))/(2**15)
                qdata1 = data[colq, :]
                signalq = adcconv*(np.ravel(qdata1.T))/(2**15)
            else:
                idata1 = data[coli, :]
                signali = np.ravel(idata1.T)
                qdata1 = data[colq, :]
                signalq = np.ravel(qdata1.T)
            
            avg = stats.trim_mean(idata1, 0.5)
            #Detect baseline by using max trigger
            [minf1, posf1] = MaxColumnWise(np.abs(idata1 - avg))

            if (posf1/npoints > 0.25):
                noisei = signali[0:bb]
                noiseq = signalq[0:bb]
            else:
                noisei = signali[npoints-bb:npoints]
                noiseq = signalq[npoints-bb:npoints]
            
            b = np.mean(noisei)
            c = np.mean(noiseq)

            [min, pos] = MinColumnWise((idata-b)**2+(qdata-c)**2)
            posbuff = np.append(posbuff, pos)

    pos = EvaluatePos(posbuff, 20)
    fmeas = f[pos]

    #if mode == 2:
    #[pos,fmeas]= dm.DataMatcher( file_name,IQfileheader,npoints,ncol,colI,colQ);

    return [pos, fmeas]



        