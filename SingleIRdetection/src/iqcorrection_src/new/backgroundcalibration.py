import numpy as np
from matplotlib import pyplot as plt
import scipy
import scipy.optimize
from scipy.interpolate import interp1d

import globvar
from datawrapper import IQCalibrationData
from utilities import Display, SameLength
from fitiqwide import FitIQWide
from ellipsefit import EllipseFit
from correctiq import CorrectIQ
from qcalc import QCalc
from correctiqbackground import CorrectIQBackground

def BackgroundCalibration(iq_calibration_data_paths, mixer, rowmin = 0, rowmax = 2000, run = 1, ifplot = 1):
    '''Load the IQ loop data and subtract the offset from the separate offset measurementì'''

    # ---------------------------- NARROW FREQUENCY RANGE --------------------------------------

    # Retrieve folders from the 'iq_calibration_data_paths' variable
    iq_narrow_off_folder = iq_calibration_data_paths[0]
    iq_narrow_on_folder = iq_calibration_data_paths[1]
    iq_wide_off_folder = iq_calibration_data_paths[2]
    iq_wide_on_folder = iq_calibration_data_paths[3]

    Display('IQ Narrow Off folder -> ' + iq_narrow_off_folder)
    Display('IQ Narrow On folder -> ' + iq_narrow_on_folder)
    Display('IQ Wide Off folder -> ' + iq_wide_off_folder)
    Display('IQ Wide On folder -> ' + iq_wide_on_folder)

    # Load data with cryostat plugged in and cold
    narrow_on_data = IQCalibrationData(iq_narrow_on_folder, rowstoskip = rowmin, rowtostop = rowmax, run_num = run)
    f_narrow_on, i_narrow_on, q_narrow_on = narrow_on_data[:, 0], narrow_on_data[:, 1], narrow_on_data[:, 2]

    # Plot IQ for the narrow frequency range
    if ifplot == 1:
        fig1, axs = plt.subplots(1, 3, figsize = (18, 5))
        fig1.suptitle('BackgroundCalibration Output')
        axs[0].plot(i_narrow_on, q_narrow_on, marker = '.', linestyle = 'None', markersize = .5, label = 'Original IQ loop')
        axs[0].plot(i_narrow_on[0], q_narrow_on[0], marker = '.', label = 'Start frequency')
        #axs[0].plot((f-fmeas)/1e9 * 100, idata**2 + qdata**2)
        axs[0].set_xlabel('I')
        axs[0].set_ylabel('Q')
        axs[0].legend()
        axs[0].set_title('Original Loop')

    # Load IQ data for the frequency swipe with the cryostat unplugged
    narrow_off_data = IQCalibrationData(iq_narrow_off_folder, rowstoskip = rowmin, rowtostop = rowmax, run_num = run)
    f_narrow_off, i_narrow_off, q_narrow_off = narrow_off_data[:, 0], narrow_off_data[:, 1], narrow_off_data[:, 2]

    # Check if the frequency ranges for the two IQ files (one with the cryostat unplugged, one with the cryostat cold) have the same lengths    
    if SameLength(f_narrow_on, f_narrow_off) == True:
        f_narrow = f_narrow_on
    else:
        Display('BackgroundCalibration -> ERROR: narrow_on and narrow_off frequencies have different lengths')

    # Subtract the noise and store I and Q in new 'idata' and 'qdata' variables
    i_narrow_on_subtract_noise = i_narrow_on - i_narrow_off
    q_narrow_on_subtract_noise = q_narrow_on - q_narrow_off

    # Plot IQ for the narrow frequency range after noise subtraction
    if ifplot == 1:
        axs[1].plot(i_narrow_on_subtract_noise, q_narrow_on_subtract_noise, marker = '.', linestyle = 'None', markersize = .5, label = 'Line noise correction')
        axs[1].plot(i_narrow_on_subtract_noise[0], q_narrow_on_subtract_noise[0], marker = 'o', label = 'Start frequency')
        #axs[1].plot((f-fmeas)/1e9 * 100, i0**2 + q0**2)
        axs[1].set_xlabel('I')
        axs[1].set_ylabel('Q')
        axs[1].legend()
        axs[1].set_title('Line Correction')

    # Correct for the mixer imperfection using results from the fit performed on the mixer calibration file
    # The data that will be corrected are Is and Qs after the noise subtraction
    [i_narrow, q_narrow] = CorrectIQ(i_narrow_on_subtract_noise, q_narrow_on_subtract_noise, mixer)

    # Plot IQ for the narrow frequency range after noise subtraction and mixer correction
    if ifplot == 1:
        axs[2].plot(i_narrow, q_narrow, marker = '.', linestyle = 'None', markersize = .5, label = 'Mixer correction')
        axs[2].plot(i_narrow[0], q_narrow[0], marker = 'o', label = 'Start frequency')
        axs[2].legend()
        axs[2].set_xlabel('I')
        axs[2].set_ylabel('Q')
        axs[2].set_title('Mixer Correction')

    # ---------------------------- WIDE FREQUENCY RANGE --------------------------------------

    # Load IQ data for the frequency swipe with the cryostat plugged in and cold and with the cryostat unplugged, this time for the wide frequency range
    wide_on_data = IQCalibrationData(iq_wide_on_folder, rowstoskip = rowmin, rowtostop = rowmax, run_num = run)
    f_wide_on, i_wide_on, q_wide_on = wide_on_data[:, 0], wide_on_data[:, 1], wide_on_data[:, 2]

    wide_off_data = IQCalibrationData(iq_wide_off_folder, rowstoskip = rowmin, rowtostop = rowmax, run_num = run)
    f_wide_off, i_wide_off, q_wide_off = wide_off_data[:, 0], wide_off_data[:, 1], wide_off_data[:, 2]

    # Check if the frequency ranges for the two IQ files (one with the cryostat unplugged, one with the cryostat cold) have the same lengths    
    if SameLength(f_wide_on, f_wide_off) == True:
        f_wide = f_wide_on
    else:
        Display('BackgroundCalibration -> ERROR: wide_on and wide_off frequencies have different lengths')

    i_wide_on_subtract_noise = i_wide_on - i_wide_off
    q_wide_on_subtract_noise = q_wide_on - q_wide_off

    [i_wide, q_wide] = CorrectIQ(i_wide_on_subtract_noise, q_wide_on_subtract_noise, mixer)

    # Crudely estimate of the resonance frequency, by observing S21 corrected data (we put the origin in the right place, nothing else)
    indexmin = np.argmin(np.square(i_narrow) + np.square(q_narrow))
    fmin = f_narrow_on[indexmin]

    # Now we fit the background through polynomials. Remember that the vector 'f' contains the frequencies 
    # near the resonance, while 'fw' contains a wide range of frequencies, including that one
    background = FitIQWide(f_wide, i_wide, q_wide, np.array([np.min(f_narrow), np.max(f_narrow)]), fmin, ifplot)

    # Use background fit parameters to adjust narrow 'S21' data
    s21corr = CorrectIQBackground(f_narrow, (i_narrow + 1j*q_narrow), background)

    if ifplot == 1:
        fig2, axs = plt.subplots(2, 3, figsize = (18, 12))
        fig2.suptitle('Background Calibration')
        axs[0, 0].plot(np.real(s21corr), np.imag(s21corr), marker = '.', linestyle = 'None', markersize = .5, label = 'Background correction')
        axs[0, 0].plot(np.real(s21corr[0]), np.imag(s21corr[0]), marker = 'o', label = 'Start IQ')
        axs[0, 0].legend()
        axs[0, 0].set_title('Background Correction')

    # Find the mixer offset at the pulse measurement frequency. We do that by fitting noise data through a linear regression
    # and then extrapolating the 'i0' and 'q0' as a function of frequencies.
    f0_i0_model = interp1d(f_narrow_off, i_narrow_off)
    f0_q0_model = interp1d(f_narrow_off, q_narrow_off)

    # We obtain offset values ('i0' and 'q0) for I and Q values at the resonance
    # (?)
    i0_extrapolated = f0_i0_model(fmin)
    q0_extrapolated = f0_q0_model(fmin)
    background.I0 = i0_extrapolated
    background.Q0 = q0_extrapolated
    
    # The IQ loop should be a circle now, but may be rotated so that it does not point toward the origin.

    # First fit to a circle (actually an ellipse)
    [r1, r2, x0, y0, phi] = EllipseFit(np.real(s21corr), np.imag(s21corr))

    def ellipse_param(x):
        '''Parametrized expression for the ellipse'''
        return x0 + r1*np.cos(x)*np.cos(phi)-r2*np.sin(x)*np.sin(phi) + 1j*(y0 + r1*np.cos(x)*np.sin(phi) + r2*np.sin(x)*np.cos(phi))
    t = np.linspace(0, 2*scipy.pi, 500)
    
    if ifplot == 1:
        axs[0, 1].plot(np.real(s21corr), np.imag(s21corr), marker = '.', linestyle = 'None', markersize = .5, label = ' Corrected S21')
        axs[0, 1].plot(np.real(ellipse_param(t)), np.imag(ellipse_param(t)), 'r', label = 'Fitting Ellipse')
        axs[0, 1].legend()
        axs[0, 1].set_title('Ellipse')

    # Now we fit for the rotation and the Q, while constraining the model to stay
    # on the circle from the previous fit
    r = np.mean([r1, r2])

    def mymodel(c, x):
        return x0 + 1j*y0 - r*np.exp(1j*(2*np.arctan(2*((x-fmin)*1e9-c[2]*1e3)*c[1]*1e-6) + c[0]))
    
    def mychi2(c):
        return np.sum(np.square(abs(s21corr - mymodel(c, f_narrow))))
    
    a0 = [0, 10, 0]

    # Find out if the points are going clockwise or counterclockwise around
    # the center of the circle and adjust the initial guess accordingly -
    # We make the 'Q' parameter initial guess negative if the slope of the
    # phase is negative

    p = np.polyfit(f_narrow - f_narrow[0], np.unwrap(np.angle(s21corr - x0 + 1j*y0)), 1)
    a0[1] = np.sign(p[0]) * a0[1]
    a = scipy.optimize.fmin(mychi2, a0)

    if ifplot == 1:
        axs[0, 2].plot(np.real(mymodel(a, f_narrow)), np.imag(mymodel(a, f_narrow)), 'g', label = 'Extrapolated Circumference')
        #axs[0, 2].plot(np.real(mymodel(a0, f_narrow)), np.imag(mymodel(a0, f_narrow)), 'g', label = 'Extrapolated Circumference')
        axs[0, 2].plot(x0, y0, 'b', marker = 'o', markersize = 2, label = 'Ellipse Center')
        #axs[0, 2].set_xlim(1.78, 1.8)
        axs[0, 2].set_aspect('equal', adjustable = 'box')
        axs[0, 2].legend()
        axs[0, 2].set_title('Model')

    off_res_point = mymodel(a, 0)

    # Loop rotation
    background.LoopRotation = np.angle(x0 + 1j*y0 - off_res_point)

    # Overall rotation
    background.OverallRotation = np.angle(off_res_point)

    # Correct with the overall rotation
    s21corr = s21corr*np.exp(-1j*background.OverallRotation)

    if ifplot == 1:
        axs[1, 0].plot(np.real(s21corr), np.imag(s21corr), marker = '.', linestyle = 'None', markersize = .5, label = 'S21 - Loop Rotation')
        axs[1, 0].plot(np.real(s21corr[0]), np.imag(s21corr[0]), 'o', marker = '.', linestyle = 'None', markersize = .5, label = 'S21 Start')
        axs[1, 0].set_aspect('equal', adjustable = 'box')
        axs[1, 0].legend()
        axs[1, 0].set_title('S21 - Loop Rotation Correction')

    # We then rotate aoround (1,0) by the angle by which the IQ loop is tilted
    # note: following the analysis of Khalil et al, arXiv:1108.3117v3, we
    # also scale the loop by the cos of the rotation angle

    print('Overall Rotation: ' + str(background.OverallRotation))
    print('Loop Rotation: ' + str(background.LoopRotation))

    #s21corr = 1 - np.cos(background.LoopRotation)*np.exp(-1j*background.LoopRotation)*(1 - s21corr)
    s21corr = 1 - abs(np.cos(background.LoopRotation))*np.exp(-1j*background.LoopRotation)*(1 - s21corr)
    
    if ifplot:
        axs[1, 1].plot(np.real(s21corr), np.imag(s21corr), 'b', marker = '.', linestyle = 'None', markersize = .5, label = 'S21 - Overall Rotation')
        axs[1, 1].plot(np.real(s21corr[0]), np.imag(s21corr[0]), marker = '.', linestyle = 'None', markersize = .5)
        axs[1, 1].plot([0, 1], 'o', label = '(0, 1)')
        axs[1, 1].plot([0, 0], 'o', label = '(0, 0)')
        axs[1, 1].set_aspect('equal', adjustable = 'box')
        axs[1, 1].legend()
        axs[1, 1].set_xlabel('I')
        axs[1, 1].set_ylabel('Q')
        axs[1, 1].set_title('S21 - Overall Rotation Correction')

    outx = np.real(s21corr)
    outy = np.imag(s21corr)

    [qtot, f0, qi, qc] = QCalc(f_narrow, outx, outy, ifplot)

    return [background, outx, outy, f_narrow, qtot, f0, qi, qc]