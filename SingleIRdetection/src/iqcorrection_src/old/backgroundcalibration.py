import numpy as np
from matplotlib import pyplot as plt
import scipy
import scipy.optimize
from scipy.interpolate import interp1d

import globvar
from displog import DispLog
from ellipsefit import EllipseFit
from loadiq import LoadIQ
from comparevector import CompareVector
from correctiq import CorrectIQ
from correctiqbackground import CorrectIQBackground
from findiqcorrection import FindIQCorrection
from qcalc import QCalc

def BackgroundCalibration(iqfileheader, mixer, fmeas, ifplot):

    checkpath = globvar.checkpath
    nchan = globvar.nchan

    if nchan == 1:
        iqname = iqfileheader[-3:]
    else:
        iqname = iqfileheader[-6:]

    # Load the IQ loop data and subtract the offset from the separate offset measurement

    # ---------------------------- NORMAL FREQUENCY RANGE --------------------------------------

    # -> Here we load IQ data for the frequency swipe with the cryostat plugged in and cold
    [f, idata, qdata] = LoadIQ(iqfileheader + '_')

    if fmeas > np.min(f) and fmeas < np.max(f):
        DispLog('- BackgroundCalibration(): OK: Correct Frequency range')
    else:
        DispLog('- BackgroundCalibration(): ERROR: Wrong Frequency range')
        #return

    # Original IQ from file
    if ifplot == 1:
        fig1, axs = plt.subplots(1, 3, figsize = (18, 5))
        fig1.suptitle('BackgroundCalibration || 1')
        axs[0].plot(idata, qdata, label = 'Original IQ loop')
        axs[0].plot(idata[0], qdata[0], marker = 'o', label = 'Start frequency')
        #axs[0].plot((f-fmeas)/1e9 * 100, idata**2 + qdata**2)
        axs[0].set_xlabel('I')
        axs[0].set_ylabel('Q')
        axs[0].legend()
        axs[0].set_title('Original Loop')

    # -> Here we load IQ data for the frequency swipe with the cryostat unplugged
    [f0, i0, q0] = LoadIQ(iqfileheader + 'off_')

    # Check if the frequency ranges for the two IQ files (one with the cryostat unplugged, one with the cryostat cold) have the same lengths    
    CompareVector(f, f0)
    idata = idata - i0
    qdata = qdata - q0

    # IQ after NOISE SUBTRACTION
    if ifplot == 1:
        axs[1].plot(idata, qdata, 'r', label = 'Line noise correction')
        axs[1].plot(idata[0], qdata[0], marker = 'o', label = 'Start frequency')
        #axs[1].plot((f-fmeas)/1e9 * 100, i0**2 + q0**2)
        axs[1].set_xlabel('I')
        axs[1].set_ylabel('Q')
        axs[1].legend()
        axs[1].set_title('Line Correction')

    # -> Here we correct for the mixer imperfection using results from the fitting performed on the calibration file, which are stored in the mixer class
    [idata, qdata] = CorrectIQ(idata, qdata, mixer)

    # IQ after MIXER CORRECTION
    if ifplot == 1:
        axs[2].plot(idata, qdata, 'g', label = 'Mixer correction')
        axs[2].plot(idata[0], qdata[0], marker = 'o', label = 'Start frequency')
        axs[2].legend()
        axs[2].set_xlabel('I')
        axs[2].set_ylabel('Q')
        axs[2].set_title('Mixer Correction')

        if checkpath:
            fig1.savefig(checkpath + '\\BackgroundCorrection_' + iqname + '_FirstCorrections.pdf', format = 'pdf')

    # ---------------------------- WIDE FREQUENCY RANGE --------------------------------------

    # -> Here we load IQ data for the frequency swipe with the cryostat plugged in and cold and with the cryostat unplugged, this time for the wide frequency range
    [fw, iw, qw] = LoadIQ(iqfileheader + 'w_')
    [f0w, i0w, q0w] = LoadIQ(iqfileheader + 'offw_')
    iw = iw - i0w
    qw = qw - q0w
    [iw, qw] = CorrectIQ(iw, qw, mixer)

    # Crudely estimate of the resonance frequency, by observing S21 slightly corrected data (we put the origin in the right place, nothing else)
    indexmin = np.argmin(np.square(idata) + np.square(qdata))
    fmin = f[indexmin]

    # Now we fit the background through polynomials. Remember that the vector 'f' contains the frequencies 
    # near the resonance, while 'fw' contains a wide range of frequencies, including that one
    background = FindIQCorrection(fw, iw, qw, np.array([np.min(f), np.max(f)]), fmin, iqfileheader, ifplot)
    s21corr = CorrectIQBackground(f, (idata + 1j*qdata), background)

    if ifplot == 1:
        fig2, axs = plt.subplots(2, 3, figsize = (18, 12))
        fig2.suptitle('Background Calibration')
        axs[0, 0].plot(np.real(s21corr), np.imag(s21corr), label = 'Background correction')
        axs[0, 0].plot(np.real(s21corr[0]), np.imag(s21corr[0]), marker = 'o', label = 'Start IQ')
        axs[0, 0].legend()
        axs[0, 0].set_title('Background Correction')

    # Find the mixer offset at the pulse measurement frequency for use later
    f0i0model = interp1d(f0, i0)
    f0q0model = interp1d(f0, q0)
    xnew = fmeas
    yi0new = f0i0model(xnew)
    yq0new = f0q0model(xnew)
    background.I0 = yi0new
    background.Q0 = yq0new
    
    # The IQ loop should be a circle now, but may be
    # Rotated so that it does not point toward the origin.
    # First fit to a circle (actually an ellipse)

    [r1, r2, x0, y0, phi] = EllipseFit(np.real(s21corr), np.imag(s21corr))

    def ellipse_param(x):
        return x0 + r1*np.cos(x)*np.cos(phi)-r2*np.sin(x)*np.sin(phi) + 1j*(y0 + r1*np.cos(x)*np.sin(phi) + r2*np.sin(x)*np.cos(phi))
    t = np.linspace(0, 2*scipy.pi, 500)
    
    if ifplot == 1:
        axs[0, 1].plot(np.real(s21corr), np.imag(s21corr), label = ' Corrected S21')
        axs[0, 1].plot(np.real(ellipse_param(t)), np.imag(ellipse_param(t)), 'r', label = 'Fitting Ellipse')
        axs[0, 1].legend()
        axs[0, 1].set_title('Ellipse')

    # Now we fit for the rotation and the Q, while constraining the model to stay
    # on the circle from the previous fit

    r = np.mean([r1, r2])

    def mymodel(c, x):
        return x0 + 1j*y0 - r*np.exp(1j*(2*np.arctan(2*(x-fmin-c[2]*1e3)*c[1]*1e-6) + c[0]))
    
    def mychi2(c):
        return np.sum(np.square(abs(s21corr - mymodel(c, f))))
    
    a0 = [0, 10, 0]

    # Find out if the points are going clockwise or counterclockwise around
    # the center of the circle and adjust the initial guess accordingly -
    # We make the 'Q' parameter initial guess negative if the slope of the
    # phase is negative

    p = np.polyfit(f - f[0], np.unwrap(np.angle(s21corr - x0 + 1j*y0)), 1)
    a0[1] = np.sign(p[0]) * a0[1]
    a = scipy.optimize.fmin(mychi2, a0)

    if ifplot == 1:
        axs[0, 2].plot(mymodel(a, f), 'g')
        axs[0, 2].set_title('Model')

    off_res_point = mymodel(a, 0)

    # Loop rotation
    background.LoopRotation = np.angle(x0 + 1j*y0 - off_res_point)

    # Overall rotation
    background.OverallRotation = np.angle(off_res_point)

    #s210 = s21corr
    s21corr = s21corr*np.exp(-1j*background.OverallRotation)

    if ifplot == 1:
        axs[1, 0].plot(np.real(s21corr), np.imag(s21corr), label = 'S21 - Loop Rotation')
        axs[1, 0].plot(np.real(s21corr[0]), np.imag(s21corr[0]), 'o', label = 'S21 Start')
        axs[1, 0].legend()
        axs[1, 0].set_title('S21 - Loop Rotation Correction')

    # We then rotate aoround (1,0) by the angle by which the IQ loop is tilted
    # note: following the analysis of Khalil et al, arXiv:1108.3117v3, we
    # also scale the loop by the cos of the rotation angle

    s21corr = 1 - np.cos(background.LoopRotation)*np.exp(-1j*background.LoopRotation)*(1 - s21corr)
    
    if ifplot:
        axs[1, 1].plot(np.real(s21corr), np.imag(s21corr), 'b', label = 'S21 - Overall Rotation')
        axs[1, 1].plot(np.real(s21corr[0]), np.imag(s21corr[0]), 'o')
        axs[1, 1].plot([0, 1], 'o', label = '(0, 1)')
        axs[1, 1].plot([0, 0], 'o', label = '(0, 0)')
        axs[1, 1].legend()
        axs[1, 1].set_xlabel('I')
        axs[1, 1].set_ylabel('Q')
        axs[1, 1].set_title('S21 - Overall Rotation Correction')

        if checkpath:
            fig2.savefig(checkpath + '\\BackgroundCorrection_' + iqname + '_SecondCorrections.pdf', format = 'pdf')
    
    outx = np.real(s21corr)
    outy = np.imag(s21corr)

    [qtot, f0, qi, qc] = QCalc(f, outx, outy, iqname, ifplot)

    return [background, outx, outy, f, qtot, f0, qi, qc]