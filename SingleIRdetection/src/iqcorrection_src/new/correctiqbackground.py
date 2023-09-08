import numpy as np

def CorrectIQBackground(f, s21data, background):
    f1 = background.FRef
    p_amp = background.PAmp
    p_phase = background.PPhase
    df = background.Df

    s21corr = s21data*(np.exp(-1j*np.polyval(p_phase, (f - f1)/df))/(np.polyval(p_amp, (f - f1)/df)))
    
    return s21corr