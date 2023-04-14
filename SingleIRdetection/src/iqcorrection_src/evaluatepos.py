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
import sys
import os


def EvaluatePos(vect, percentage):
    global logpath

    vect = np.array(vect)
    vect = np.sort(vect)
    dell = np.int32(round(len(vect)*percentage/200))
    vect = vect[dell-1: len(vect) - dell]
    pos = round(np.mean(vect))
    lndev = np.abs(np.array(vect - pos))

    try:
        logpath
    except NameError:
        logpath = str(os.getcwd() + '/logfile.log')
        
    fid = open(logpath, 'a')
    original_stdout = sys.stdout
    sys.stdout = fid  #Change the standard output to the file we created.

    if np.mean(lndev) > 0.5:
        print('- EvaluatePos(): ERROR: working point frequency is unstable: ' + str(np.mean(lndev)))
    else:
        print('- EvaluatePos(): OK: working point frequency is stable: ' + str(np.mean(lndev)))

    sys.stdout = original_stdout   
    fid.close()
    return pos