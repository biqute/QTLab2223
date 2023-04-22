import numpy as np
import findiqcorrection as fiq

def CorrectIQBackground(f, s21data, background):

    f1 = background.FRef
    p_amp = background.PAmp
    p_phase = background.PPhase
    df = background.Df

    s21corr = np.multiply(s21data, np.divide(np.exp(-1j*np.polyval(p_phase, (f - f1)/df)), np.polyval(p_amp, (f - f1)/df)))
    return s21corr