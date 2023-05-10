import numpy as np
from scipy import linalg
import math
from mathfunctions import ElementWiseProd

def EllipseFit(x, y):
    #
    # ellipse_fit - Given a set of points (x,y), ellipse_fit returns the
    # best-fit ellipse (in the Least Squares sense) 
    #
    # Input:                  
    #                       x - a vector of x measurements
    #                       y - a vector of y measurements
    #
    # Output:
    #
    #                   semimajor_axis - Magnitude of ellipse longer axis
    #                   semiminor_axis - Magnitude of ellipse shorter axis
    #                   x0 - x coordinate of ellipse center 
    #                   y0-  y coordinate of ellipse center 
    #                   phi - Angle of rotation in radians with respect to
    #                   the minor axis
    #
    # Algorithm used:
    #
    # Given the quadratic form of an ellipse: 
    #  
    #       a*x^2 + 2*b*x*y + c*y^2  + 2*d*x + 2*f*y + g = 0   (1)
    #                          
    #  we need to find the best (in the Least Square sense) parameters a,b,c,d,f,g. 
    #  To transform this into the usual way in which such estimation problems are presented,
    #  divide both sides of equation (1) by a and then move x^2 to the
    # other side. This gives us:
    #
    #       2*b'*x*y + c'*y^2  + 2*d'*x + 2*f'*y + g' = -x^2            (2)
    #  
    #   where the primed parametes are the original ones divided by a.
    #  Now the usual estimation technique is used where the problem is
    #  presented as:
    #
    #    M * p = b,  where M = [2*x*y y^2 2*x 2*y ones(size(x))], 
    #    p = [b c d e f g], and b = -x^2. We seek the vector p, given by:
    #    
    #    p = pseudoinverse(M) * b.
    #  
    #    From here on I used formulas (19) - (24) in Wolfram Mathworld:
    #    http://mathworld.wolfram.com/Ellipse.html
    #
    #
    # Programmed by: Tal Hendel <thendel@tx.technion.ac.il>
    # Faculty of Biomedical Engineering, Technion- Israel Institute of Technology     
    # 12-Dec-2008
    #
    #--------------------------------------------------------------------------

    x = np.array(x)
    y = np.array(y)
    x = x.reshape((-1, 1))
    y = y.reshape((-1, 1))
    ones = np.ones(len(x))
    elementwiseprod = ElementWiseProd(x, y)
    M = np.hstack((2*elementwiseprod, np.square(y), 2*x, 2*y, ones.reshape((-1, 1))))
    M = linalg.pinv(M)
    least_squares_output = linalg.solve(M, -np.square(x))
    parameters = M * (-np.square(x))
    print(parameters)

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
