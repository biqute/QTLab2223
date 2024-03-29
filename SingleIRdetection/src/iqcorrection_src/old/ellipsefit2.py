import numpy as np
import numpy.linalg as linalg
import matplotlib.pyplot as plt

def fitEllipse(x,y):
    x = x[:, np.newaxis]    
    y = y[:, np.newaxis]    #Transpose 'x' and 'y' vectors
    D = np.hstack((x*x, x*y, y*y, x, y, np.ones_like(x)))   #Declares an array of ones with the same length as 'x'
    S = np.dot(D.T,D)
    C = np.zeros([6, 6])
    C[0,2] = C[2,0] = 2; C[1,1] = -1
    E, V =  linalg.eig(np.dot(linalg.inv(S), C))
    n =  np.argmax(np.abs(E))
    a = V[:,n]
    return a

def ellipse_center(a):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    num = b*b-a*c
    x0=(c*d-b*f)/num
    y0=(a*f-b*d)/num
    return np.array([x0, y0])

def ellipse_angle_of_rotation( a ):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    return 0.5*np.arctan(2*b/(a-c))

def ellipse_axis_length( a ):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    up = 2*(a*f*f+c*d*d+g*b*b-2*b*d*f-a*c*g)
    down1 = (b*b-a*c)*((c-a)*np.sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a))
    down2 = (b*b-a*c)*((a-c)*np.sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a))
    res1 = np.sqrt(up/down1)
    res2 = np.sqrt(up/down2)
    semimajor = max(res1, res2)
    semiminor = min(res1, res2)
    return np.array([semiminor, semimajor])

def EllipseFit2(x, y):
    xmean = x.mean()
    ymean = y.mean()
    x = x - xmean
    y = y - ymean
    a = fitEllipse(x,y)
    center = ellipse_center(a)
    center[0] += xmean
    center[1] += ymean
    phi = ellipse_angle_of_rotation(a)
    axes = ellipse_axis_length(a)
    semiminor = axes[0]
    semimajor = axes[1]
    x += xmean
    y += ymean
    return [semiminor, semimajor, center[0], center[1], phi]