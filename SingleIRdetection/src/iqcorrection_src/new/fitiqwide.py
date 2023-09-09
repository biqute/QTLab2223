import numpy as np
from matplotlib import pyplot as plt

class Background:
        PAmp = 0
        PPhase = 0
        Df = 0
        FRef = 0
        I0 = 0
        Q0 = 0
        LoopRotation = 0
        OverallRotation = 0

def FitIQWide(f_wide, i_wide, q_wide, f_window, fmin, ifplot):

    f_window = np.array(f_window)

    # We translate the origin: now it concides with 'fmin'
    f_wide = f_wide - fmin
    f_window = f_window - fmin
    f_windowfact = 1
    f_window = f_window*f_windowfact
    
    # Degree for the fitting polynomial
    bgpoldeg = 5

    # In order to fit the background we want to consider frequencies out of the resonance. We want to fit background noise!

    # In the wide frequency range, this translates into not considering the small frequency range. 
    ii = np.where(np.logical_or(f_wide < f_window[0], f_wide > f_window[1]))
    f_wide_window = f_wide[-1] - f_wide[0]

    # We define the speed of light
    c = 3e8 

    # First determine the amplitude variation of the background with frequency
    p_amp = np.polyfit(f_wide[ii]/f_wide_window, np.absolute(i_wide[ii] + 1j*q_wide[ii]), bgpoldeg)
    ref = [np.mean(np.absolute(i_wide + 1j*q_wide)), np.mean(np.absolute(i_wide + 1j*q_wide))]

    if ifplot == 1:
        fig, axs = plt.subplots(1, 3, figsize = (18, 5))
        fig.suptitle('FitIQWide')
        axs[0].plot(f_wide, np.absolute(i_wide + 1j*q_wide), label = 'Abs(I,Q)')
        axs[0].plot(f_wide, np.polyval(p_amp, f_wide/f_wide_window), label = 'Background Fit')
        axs[0].plot(f_window, ref, 'o', 'g')
        axs[0].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[0].set_ylabel('ADC values')
        axs[0].set_title('S21 Background Fit')
        axs[0].legend()

    # Now determine the phase variation with frequency
    p_phase = np.polyfit(f_wide[ii]/f_wide_window, np.angle(i_wide[ii] + 1j*q_wide[ii]), bgpoldeg)
    
    if ifplot == 1:
        axs[1].plot(f_wide, np.angle(i_wide + 1j*q_wide), label = 'Angle(I, Q)')
        axs[1].plot(f_wide, np.polyval(p_phase, f_wide/f_wide_window), label = 'Background Phase')
        axs[1].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[1].set_ylabel('Angle (rad)')
        axs[1].set_title('Phase Background Fit')
        axs[1].legend()

    # (?)
    def mymodel(a, b, ddf):
        return np.polyval(a, ddf/f_wide_window)*np.exp(1j*np.polyval(b, ddf/f_wide_window))
    
    if ifplot == 1:
        axs[2].plot(f_wide, i_wide, label = 'I')
        axs[2].plot(f_wide, q_wide, label = 'Q')
        axs[2].plot(f_wide, np.real(mymodel(p_amp, p_phase, f_wide)), 'r', label = 'Real Part of Background Fit')
        axs[2].plot(f_wide, np.imag(mymodel(p_amp, p_phase, f_wide)), 'm', label = 'Imaginary Part of Background Fit')

        #axs[2].plot(f_wide, np.real(np.absolute(i_wide + 1j*q_wide)*mymodel(p_amp, p_phase, f_wide)), 'r', label = 'Real Part of Background Fit')

        axs[2].set_xlabel('Frequency - Resonance Frequency (Hz)')
        axs[2].set_ylabel('ADC values')
        axs[2].set_title('I and Q Background Fit')
        axs[2].legend()

    background = Background()
    background.PAmp = p_amp
    background.PPhase = p_phase
    background.Df = f_wide_window
    background.FRef = fmin

    return background