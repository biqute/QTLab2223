import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt

import globvar

def QCalc(f, i, q, ifplot):

    gain = 1
    color = 1
    i = i/gain
    q = q/gain
    win = [i for i in range(len(f))]
    #i=i+mean(i(win(1):win(10))); q=q+mean(q(win(1):win(10)));

    smag = np.zeros([1, len(win)])    #sdB=smag; fp=smag; ff=smag;

    #map = colormap( jet(color));

    smag = np.sqrt(np.square(i) + np.square(q))
    smag = smag / np.mean(smag[win[0]: win[9]])
    ff = f[win]
    sma = smag[win]
    sdB = 20*np.log10(sma)

    if ifplot == 1:
        plt.plot(ff, sdB, 'r', linewidth = 1.5)
        plt.title('QCalc -> S Magnitude')
        plt.show()

    smin = np.min(sma)
    ii = np.where(sma == smin)
    fmin = ff[ii]
    fp = ff - fmin

    def mymodel(fp, c):
        return abs(c[5]*fp + c[0]*(1 - np.exp(1j*c[4])*c[1]*(c[1]**-1 - abs(c[2])**-1) / (1 + 2j*c[1]*(fp - c[3])/fmin)))
    
    #Weigh more the bottom of dips
    def mychi2(fp, c):
        return np.sum(((np.square(abs(mymodel(fp, c) - sma))) / np.square(abs(sma))))

    a0 = np.zeros(6)
    a0[0] = 1
    a0[1] = 4e3
    a0[2] = 4e3
    a0[3] = 0
    a0[4] = 0
    a0[5] = -1e-9
    result = minimize(mychi2, fp, args = a0)
    a = result.x

    qtot = abs(a[1])
    qi = abs(a[2])
    qc = 1 / (1/qtot - 1/qi)
    f0 = a[3] + fmin

    #sdbfit = 20*np.log10(mymodel(fp, a))   #(fix)
    
    #if ifplot
    #plot( ff, sdB_fit, 'k--')
    #print(GR,'-dpdf',[checkpath,'/ResonanceFit',IQname,'.pdf'])

    return [qtot, f0, qi, qc]