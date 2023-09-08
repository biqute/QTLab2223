import numpy as np

def CorrectIQ(idata, qdata, mixer):

    ''' Correct IQ data to fix the mixer imperfection
    usage:  [Icor, Qcor] = CorrectIQ( idata, qdata, mixer)
    inputs:
    idata -     I quadrature
    qdata -     Q quadrature
    mixer -     structure returned by calIQ after the calibration file fitting
    outputs:
    Icor -      corrected I
    Qcor -      corrected Q '''

    AI = mixer.AI
    AQ = mixer.AQ
    gamma = mixer.Gamma

    g = AI * qdata / (AQ * idata)
    theta = np.zeros(idata.shape)
    r = theta.copy()

    II = idata >= 0
    theta[II] = np.arctan((np.cos(gamma) - g[II]) / np.sin(gamma))
    II = idata < 0
    theta[II] = np.arctan((np.cos(gamma) - g[II]) / np.sin(gamma)) - np.pi

    II = np.abs(np.cos(theta)) >= 0.5
    r[II] = idata[II] / (AI * np.cos(theta[II]))
    II = np.abs(np.cos(theta)) < 0.5
    r[II] = qdata[II] / (AQ * np.cos(theta[II] + gamma))

    Icor = r * np.sqrt(AI * AQ) * np.cos(theta)
    Qcor = r * np.sqrt(AI * AQ) * np.sin(theta)

    Icor = np.reshape(Icor, idata.shape)
    Qcor = np.reshape(Qcor, qdata.shape)

    return [Icor, Qcor]
    

      
   
