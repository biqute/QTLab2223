from scipy import stats
import numpy as np

import loadiq as liq
import globvar

def CorrSynt(iqfileheader, signali, signalq, mode, recnum, channel, pos, ifplot):
    #CORR_SYNT Summary of this function goes here
    #   Detailed explanation goes here
    
    checkpath = globvar.checkpath

    [f, idata, qdata] = liq.LoadIQ(iqfileheader + '_')
    recordlength = len(signali)
    avg = stats.trim_mean(signali,50)

    #detecting baseline by max trigger

    [minf1, posf1] = np.max(abs(signali - avg))
    
    bb = np.int32(round(recordlength))

    if (posf1/recordlength > 0.25):
        noisei = signali[0:bb]
        noiseq = signalq[0:bb]
    else:
        noisei = signali[recordlength - bb - 1: recordlength - 1]
        NoiseQ = signalq[recordlength - bb - 1: recordlength - 1]

    b = np.mean(noisei)
    c = np.mean(noiseq)

    #Mode 0 traslation to the resonance point
    #Mode 1 traslation to the nearest point of the circle
    if mode == 0:
        s21 = np.square(idata) + np.square(qdata)
        [min, res] = [np.min(s21), s21.index(np.min(s21))] 

    if mode == 1:
        s21 = np.square(idata - b) + np.square(qdata - c)
        [min, res] = [np.min(s21), s21.index(np.min(s21))]

    if mode == 2:
        res = pos

    ti = idata[res] - b
    tq = qdata[res] - b
    a = [ti, tq]
    corri = signali + ti
    corrq = signalq + tq

    if mode == 2:
        res = np.append(res, f[res])
    
    return [corri, corrq, a, res]
