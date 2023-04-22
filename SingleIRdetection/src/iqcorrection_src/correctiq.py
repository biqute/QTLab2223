import numpy as np
import scipy

def CorrectIQ(idata, qdata, mixer):

#Corrects IQ data for the mixer imperfection
#usage:  [Icor, Qcor] = CorrectIQ( Idata, Qdata, mixer)
#inputs:
#   Idata -     I quadrature
#   Qdata -     Q quadrature
#   mixer -     structure returned by cal_IQ.m
#outputs:
#   Icor -      corrected I
#   Qcor -      corrected Q

    ai = mixer.AI
    aq = mixer.AQ
    gamma = mixer.gamma

    g = np.divide(ai*qdata, aq*idata)
    theta = 0*idata
    r = theta

    ii = np.argwhere(idata >= 0)
    theta[ii] = np.arctan(np.divide((np.cos(gamma) - g[ii]), np.sin(gamma)))
    ii = np.argwhere(idata < 0)
    theta[ii] = np.arctan(np.divide((np.cos(gamma) - g[ii]), np.sin(gamma))) - scipy.pi

    ii = np.argwhere(abs(np.cos(theta)) >= 0.5)
    r[ii] = np.divide(idata[ii], (ai*np.cos(theta[ii])))
    ii = np.argwhere(abs(np.cos(theta)) < 0.5)
    r[ii] = np.divide(qdata[ii], (aq * np.cos(theta[ii] + gamma)))

    icor = np.multiply(r*np.sqrt(np.multiply(ai, aq)), np.cos(theta))
    qcor = np.multiply(r*np.sqrt(np.multiply(ai, aq)), np.sin(theta))

    icor = np.reshape(icor, np.shape(idata), 'F')   #(?) Fortran - like index ordering should recall matlab reshape function
    qcor = np.reshape(qcor, np.shape(qdata), 'F')   #(?) Fortran - like index ordering should recall matlab reshape function
    

      
   
