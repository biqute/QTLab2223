import globvar
import sys
import re

def NumbersInString(string):
    '''Returns all numbers in input string'''
    numbers = re.findall(r'\d+(\.\d+)?', string)
    return [float(num) for num in numbers]

def Display(message):
    logpath = globvar.logpath
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

def CorrectionLog(setup):
    ''' This function prints the conversion log. Information is given via the setup variable.
        Order of information stored in setup is the following:
        [0] Channels Number, [1] Number Of Events, [2] Event Length'''
    
    Display('Number of Channels = ' + str(setup[0]) + '\n')
    Display('Number Of Events = ' + str(setup[1]) + '\n')
    Display('Event Length = ' + str(setup[2]) + '\n')
    Display('Mixer Calibration File = ' + str(setup[3]) + '\n')
    return