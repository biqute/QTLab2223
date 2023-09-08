import globvar
import sys
import re

def SameLength(a, b):
    if len(a) == len(b):
        return True
    else:
        return False

def NumbersInString(string):
    '''Returns all numbers in input string'''
    numbers = re.findall(r'\d+(?:\.\d+)?', string)
    return [float(num) for num in numbers]

def SumStringsToStringArray(leftstring, stringarray, rightstring):
    '''Transforms every elemeny of a string array in a new string, to which 'leftstring' is added to the left and 'rightstring' is added to the right'''
    summedstring = []
    for element in stringarray:
        summedstring.append(leftstring + element + rightstring)
    return summedstring

def Display(message, analysis_run = 1):
    import os
    from datetime import date
    today = date.today()
    logpath = globvar.logpath + '_run' + str(analysis_run) +'_' + str(today) + '.log'

    if logpath:
        original = sys.stdout
        fid = open(logpath, 'a')
        sys.stdout = fid
        print(message)
        sys.stdout = original
        fid.close()
    else:
        print(message)
    return 

def CorrectionLog(setup, run = 1):
    ''' This function prints the conversion log. Information is given via the setup variable. Order is given by the structure of correction.py script'''
    
    Display('Number of Channels = ' + str(setup[0]), analysis_run = run)
    Display('Number of Events = ' + str(setup[1]), analysis_run = run)
    Display('Event Length = ' + str(setup[2]), analysis_run = run)
    Display('Mixer Calibration File = ' + str(setup[3]) + '\n', analysis_run = run)
    Display(' ------------------------- Mixer Calibration Output -------------------------', analysis_run = run)
    Display('[Mixer] AI = ' + str(setup[4]), analysis_run = run)
    Display('[Mixer] AQ = ' + str(setup[5]), analysis_run = run)
    Display('[Mixer] I0 = ' + str(setup[6]), analysis_run = run)
    Display('[Mixer] Q0 = ' + str(setup[7]), analysis_run = run)
    Display('[Mixer] Amp = ' + str(setup[8]), analysis_run = run)
    Display(' ------------------------- Mixer Calibration Output -------------------------\n', analysis_run = run)

    Display(' ------------------------- IQ Calibration Output -------------------------', analysis_run = run)
    
    Display(' ------------------------- IQ Calibration Output -------------------------', analysis_run = run)

    return