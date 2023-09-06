#The following function allows to eliminate a certain percentage (equally in left and right) of a vector entries.
#It then computes the average value of the remaining terms and establishes if 
#the WorkPoint frequency is stable 
#----------------------------------------------
#input: 
#   - vect is the vector we want to analyse
#   - percentage is the percentage of entries we are going to trim out
#output: the average value of vect entries
#----------------------------------------------
#you can try to run the function in terms of your local directory. You can modify and uncomment the following:

#logpath = 'C:/Users/alexb/Desktop/Save/prova.log'

import numpy as np
from displog import DispLog

def EvaluatePos(vector, percentage):

    vec = np.sort(np.array(vector))
    dell = np.int32(round(len(vec)*percentage/200))

    if dell >= 1:
        vec = vec[dell - 1:  - dell - 1]

    pos = round(np.mean(vec))
    lndev = np.abs(np.array(vec - pos))

    meanlndev = np.mean(lndev)
    
    if meanlndev > 0.5:
        DispLog('- EvaluatePos(): ERROR: working point frequency is unstable: ' + str(meanlndev))
    else:
        DispLog('- EvaluatePos(): OK: working point frequency is stable: ' + str(meanlndev))

    return pos