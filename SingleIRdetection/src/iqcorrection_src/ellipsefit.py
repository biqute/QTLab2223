import numpy as np
from scipy import linalg
import math
from mathfunctions import ElementWiseProd

def EllipseFit(x, y):

    x = np.array(x)
    y = np.array(y)
    x = x.reshape((-1, 1))
    y = y.reshape((-1, 1))
    ones = np.ones(len(x))
    elementwiseprod = ElementWiseProd(x, y)
    M = np.hstack((2*elementwiseprod, np.square(y), 2*x, 2*y, ones.reshape((-1, 1))))
    least_squares_output = linalg.lstsq(M, -np.square(x))
    parameters = least_squares_output[0]

    #Extract parameters from parameters vector
    a = 1
    b = parameters[0]
    c = parameters[1]
    d = parameters[2]
    f = parameters[3]
    g = parameters[4]

    #Use Formulas from Mathworld to find semimajor_axis, semiminor_axis, x0, y0 and phi
    delta = b**2-a*c
    x0 = (c*d - b*f)/delta
    y0 = (a*f - b*d)/delta
    phi = 0.5 * math.atan((2*b)/(c-a))

    nom = 2*(a*f**2 + c*d**2 + g*b**2 - 2*b*d*f - a*c*g)
    s = math.sqrt(1 + (4*b**2)/(a-c)**2)

    a_prime = math.sqrt(nom/(delta*((c-a)*s - (c+a))))

    b_prime = math.sqrt(nom/(delta*((a-c)*s - (c+a))))

    semimajor_axis = max(a_prime, b_prime)
    semiminor_axis = min(a_prime, b_prime)

    if (a_prime < b_prime):
        phi = (math.pi)/2 + phi

    return [semimajor_axis, semiminor_axis, x0, y0, phi]
