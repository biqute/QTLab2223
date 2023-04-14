#The following function loads data from files. Output information will be printed
#in a log file located at "logpath"
#----------------------------------------------
#input: path relative to basename in which .txt data files are stored
#output: three vectors containing, respectively: frequencies (first file), I (second file) and Q (third file)
#----------------------------------------------
#you can try to run the function in terms of your local directory. You can modify and uncomment the following:

#logpath = 'C:/Users/alexb/Desktop/Save/prova.log'

import sys
import os
import numpy as np

def LoadIQ(basename):
    original_stdout = sys.stdout    #Save a reference to the original standard output
    global logpath

    try:
        logpath
    except NameError:
        logpath = str(os.getcwd() + '/logfile.log')

    fid = open(logpath, 'a')
    original_stdout = sys.stdout
    sys.stdout = fid  #Change the standard output to the file we created.

    if os.path.exists(basename + '/0.txt'):
        print('- LoadIQ(): OK: frequency file loaded: ' + basename + '0.txt')
    else:
        print('- LoadIQ(): ERROR: ' + basename + '0.txt not found')
        return []
    
    if os.path.exists(basename + '/1.txt'):
        print('- LoadIQ(): OK: frequency file loaded: ' + basename + '1.txt')
    else:
        print('- LoadIQ(): ERROR: ' + basename + '1.txt not found')
        return []

    if os.path.exists(basename + '/2.txt'):
        print('- LoadIQ(): OK: frequency file loaded: ' + basename + '2.txt')
    else:
        print('- LoadIQ(): ERROR: ' + basename + '2.txt not found')
        return []

    sys.stdout = original_stdout
    fid.close()

    f = np.loadtxt(basename + '/0.txt')
    idata = np.loadtxt(basename + '/1.txt')
    qdata = np.loadtxt(basename + '/2.txt')

    return [f, idata, qdata]
