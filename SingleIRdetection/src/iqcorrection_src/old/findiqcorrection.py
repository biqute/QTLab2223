import numpy as np
from matplotlib import pyplot as plt

import globvar

 # Fit a wide range IQ scan to remove background variations of the microwave transmission
    #
    #How to:  [p_amp, p_phase, Df] = find_iq_correction(fw, iw, qw, xwin, f1)

    #Inputs:

    #   fw -        IQ scan frequency data
    #   iw -        I data
    #   qw -        Q data
    #   xwin -      Two element vector of frequencies to exclude from the fit
    #               (because this is where the resonance is)
    #   f1 -        an arbitrary frequency offset - make this approximately the
    #               resonance frequency
    #Outputs:

    # background: a structure containing the background fit info
    #       .p_amp -     polynomial fit to the magnitude
    #       .p_phase -   polynomial fit to the phase
    #       .Df -        total frequency scan used for scaling

class Background:
        PAmp = 0
        PPhase = 0
        Df = 0
        FRef = 0
        I0 = 0
        Q0 = 0
        LoopRotation = 0
        OverallRotation = 0

def FindIQCorrection(fw, iw, qw, xwin, f1, iqfileheader, ifplot):

    checkpath = globvar.checkpath
    nchan = globvar.nchan

    xwin = np.array(xwin)

    # We translate the origin: now it concides with f1
    fw = fw - f1
    xwin = xwin - f1
    xwinfact = 1
    xwin = xwin*xwinfact
    # We define the degree of the fitting polynomial
    bgpoldeg = 5

    # In order to fit the background we want to consider frequencies out of the resonance. In the wide frequency range,
    # this translates into not considering the small frequency range
    ii = np.where(np.logical_or(fw < xwin[0], fw > xwin[1]))
    df = fw[-1] - fw[0]

    # We define the speed of light
    c = 3e8 

    # First determine the amplitude variation of the background with frequency
    p_amp = np.polyfit(fw[ii]/df, abs(iw[ii] + 1j*qw[ii]), bgpoldeg)
    ref = [np.mean(abs(iw + 1j*qw)), np.mean(abs(iw + 1j*qw))]

    if nchan == 1:
        iqname = iqfileheader[-3:]
    else:
        iqname = iqfileheader[-6:]

    if ifplot == 1:
        fig, axs = plt.subplots(1, 3, figsize = (18, 5))
        fig.suptitle('FindIQCorrection')
        axs[0].plot(fw, np.absolute(iw + 1j*qw), label = 'Abs(I,Q)')
        axs[0].plot(fw, np.polyval(p_amp, fw/df), label = 'Background Fit')
        axs[0].plot(xwin, ref, 'o', 'g')
        axs[0].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[0].set_ylabel('ADC values')
        axs[0].set_title(iqname + ' S21 Background Fit')
        axs[0].legend()

    #Now determine the phase variation with frequency
    p_phase = np.polyfit(fw[ii]/df, np.unwrap(np.angle(iw[ii] + 1j*qw[ii])), 1)
    
    if ifplot == 1:
        axs[1].plot(fw, np.unwrap(np.angle(iw + 1j*qw)), label = 'Angle(I, Q)')
        axs[1].plot(fw, np.polyval(p_phase, fw/df), label = 'Background Phase')
        axs[1].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[1].set_ylabel('Angle (rad)')
        axs[1].set_title(iqname + ' Phase Background Fit')
        axs[1].legend()

    def mymodel(a, b, ddf):
        return np.polyval(a, ddf/df)*np.exp(1j*np.polyval(b, ddf/df))
    
    if ifplot == 1:
        axs[2].plot(fw, iw, label = 'I')
        axs[2].plot(fw, qw, label = 'Q')
        axs[2].plot(fw, np.real(mymodel(p_amp, p_phase, fw)), 'r', label = 'Real Part of Background Fit')
        axs[2].plot(fw, np.imag(mymodel(p_amp, p_phase, fw)), 'm', label = 'Imaginary Part of Background Fit')
        axs[2].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[2].set_ylabel('ADC values')
        axs[2].set_title(iqname + ' I and Q Background Fit')
        axs[2].legend()

        fig.savefig(checkpath + '\\BackgroundFitPhase_' + iqname + '.pdf', format = 'pdf')
         
    background = Background()
    background.PAmp = p_amp
    background.PPhase = p_phase
    background.Df = df
    background.FRef = f1

    return background