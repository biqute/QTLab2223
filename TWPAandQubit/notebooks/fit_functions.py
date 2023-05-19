from scipy.optimize import curve_fit
import numpy as np

def lorentz(x, x0, gamma, A, offset):
    return offset + (A/gamma)/(((x-x0)/gamma)**2 + 1)

def pol_lorentz(x, x0, gamma, A, offset, p1, p2, p3, p4, fmin, fmax):
    return lorentz(x, x0, gamma, A, offset) + (np.polyval([p4,p3,p2,p1,0],x-fmin))*(x>fmin)*(x<fmax)

def double_lorentz(x,x0,y0,g1,g2,A1,A2):
    return (A1/g1)*(1/(1+((x-x0)/g1)**2)) + (A2/g2)*(1/(1+((x-y0)/g2)**2))

def parabola(x,x0,y0,A):
    return y0+A*(x-x0)**2 