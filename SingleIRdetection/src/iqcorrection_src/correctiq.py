import numpy as np

def CorrectIQ(Idata, Qdata, mixer):

# Correct IQ data for the mixer imperfection
# usage:  [Icor, Qcor] = CorrectIQ( Idata, Qdata, mixer)
# inputs:
#   Idata -     I quadrature
#   Qdata -     Q quadrature
#   mixer -     structure returned by cal_IQ.m
# outputs:
#   Icor -      corrected I
#   Qcor -      corrected Q

    AI = mixer.AI
    AQ = mixer.AQ
    gamma = mixer.Gamma

    g = AI * Qdata / (AQ * Idata)
    theta = np.zeros(Idata.shape)
    r = theta.copy()

    II = Idata >= 0
    theta[II] = np.arctan((np.cos(gamma) - g[II]) / np.sin(gamma))
    II = Idata < 0
    theta[II] = np.arctan((np.cos(gamma) - g[II]) / np.sin(gamma)) - np.pi

    II = np.abs(np.cos(theta)) >= 0.5
    r[II] = Idata[II] / (AI * np.cos(theta[II]))
    II = np.abs(np.cos(theta)) < 0.5
    r[II] = Qdata[II] / (AQ * np.cos(theta[II] + gamma))

    Icor = r * np.sqrt(AI * AQ) * np.cos(theta)
    Qcor = r * np.sqrt(AI * AQ) * np.sin(theta)

    Icor = np.reshape(Icor, Idata.shape)
    Qcor = np.reshape(Qcor, Qdata.shape)

    return [Icor, Qcor]
    

      
   
