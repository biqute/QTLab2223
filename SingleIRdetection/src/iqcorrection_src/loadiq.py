
from os import path
import numpy as np
import globvar

from displog import DispLog

def LoadIQ(basename):

    if path.exists(basename + '0.txt'):
        DispLog('- LoadIQ(): OK: frequency file loaded: ' + basename + '0.txt')
    else:
        DispLog('- LoadIQ(): ERROR: ' + basename + '0.txt not found')
        return []
    
    if path.exists(basename + '1.txt'):
        DispLog('- LoadIQ(): OK: frequency file loaded: ' + basename + '1.txt')
    else:
        DispLog('- LoadIQ(): ERROR: ' + basename + '1.txt not found')
        return []

    if path.exists(basename + '2.txt'):
        DispLog('- LoadIQ(): OK: frequency file loaded: ' + basename + '2.txt')
    else:
        DispLog('- LoadIQ(): ERROR: ' + basename + '2.txt not found')
        return []

    f = np.loadtxt(basename + '0.txt')
    idata = np.loadtxt(basename + '1.txt')
    qdata = np.loadtxt(basename + '2.txt')

    return [f, idata, qdata]
