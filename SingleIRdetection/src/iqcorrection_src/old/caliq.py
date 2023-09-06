import math
import numpy as np
from matplotlib.patches import Ellipse

import globvar
from matplotlib import pyplot as plt
from ellipsefit import EllipseFit
from readdata import ReadData
from correctiq import CorrectIQ


class Mixer:
    Gamma = 0
    AI = 0
    AQ = 0
    I0 = 0
    Q0 = 0
    Amp = 0

def Cal_IQ(mixercalfile, icol, qcol, ifplot):

    #Function to read the IQ mixer calibration file, fit to an ellipse and
    #calculate the correction coefficients.  See the appendix of Jiansong Gao's
    #thesis (pag. 162) for the equations and further description.

    #Inputs:
    #   mixercalfile -  calibration data file
    #   xcol -      the column in the file corresponding to the I quadrature
    #   ycol -      Q quadrature
    #   ifplot -    1 if you want to see the plot

    #Outputs:
    #   mixer -     structure with coefficients used for correction
    #       .AI     I quadrature gain
    #       .AQ     Q quadrature gain
    #       .gamma  phase between quadratures

    recordlength = globvar.recordlength

    [idata, qdata] = ReadData(mixercalfile, icol, qcol)
    
    # we want to fit the ellipse from the calibration file in order to obtain the parameters to fix our non - ideal mixer
    [semimajor_axis, semiminor_axis, i0, q0, phi] = EllipseFit(idata, qdata)

    a = semimajor_axis
    b = semiminor_axis
    th = np.linspace(0, 2*np.pi, 200)

    ai = math.sqrt((a**2)*(np.cos(phi))**2 + (b**2)*(np.sin(phi))**2)
    ai = math.sqrt((a**2)*np.square(np.cos(phi)) + (b**2)*np.square((np.sin(phi))))
    aq = math.sqrt((a**2)*np.square((np.sin(phi))) + (b**2)*np.square((np.cos(phi))))
    alpha1 = math.atan((b*np.sin(phi)/(a*np.cos(phi))))
    alpha2 = math.pi - math.atan((b*np.cos(phi))/(a*np.sin(phi)))
    gamma = alpha1 - alpha2

    #Radius of corrected I/Q loop
    mixer = Mixer()
    mixer.Gamma = gamma
    mixer.AI = ai
    mixer.AQ = aq
    mixer.I0 = i0
    mixer.Q0 = q0

    [icor, qcor] = CorrectIQ(idata - i0, qdata - q0, mixer)

    amp = np.mean(np.sqrt(np.square(np.array(icor)) + np.square(np.array(qcor))))
    mixer.Amp = amp

    if icol == 0:
        nch = 1
    else:
        nch = 2

    if ifplot == 1:
        plt.figure(figsize=(10,10))
        x = ai * np.cos(th)
        y = aq * np.cos(th + gamma)
        plt.plot(idata, qdata, 'b', label = "Cal Data")
        plt.plot(i0 + x, q0 + y, 'r', label = "Cal Data Fit")
        plt.plot(icor + i0, qcor + q0, 'g', label = 'Correction')
        plt.legend(loc = 'upper left')
        plt.title('CalIQ() -> IQ Calibration Plot for channel ' + str(nch))
        plt.axis('scaled')
        plt.show()

    return mixer
    

