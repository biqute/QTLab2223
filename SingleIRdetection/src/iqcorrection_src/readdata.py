import numpy as np
import globvar
import sys

def ReadData(filename, ncol, icol, qcol, start, npoints):

    logpath = globvar.logpath
    originalpoints = int(globvar.recordlength)
    ncol = int(ncol)
    npoints = int(npoints)

    #actually, as you can see, we don't need to specify the number of points in order to properly store data from file

    data = np.loadtxt(filename, dtype = float, delimiter = '\t')
    datapoints = data.shape[0]

    if datapoints < globvar.recordlength:
        if logpath:
            original = sys.stdout
            log = open(logpath, 'a')
            sys.stdout = log
            print('- ReadData(): WARNING: The number of points from the setup file is greater than the actual record length for file: ' + filename)
            sys.stdout = original
            log.close()
        else:
            print('- ReadData(): WARNING: The number of points from the setup file is greater than the actual record length for file: ' + filename)

    start = start

    idata = np.array(data[:, icol])
    qdata = np.array(data[:, qcol])

    if (len(idata) == len(qdata)):
        if logpath:
            original = sys.stdout
            log = open(logpath, 'a')
            sys.stdout = log
            print('- ReadData(): OK: The two data arrays have the same length for file: ' + filename)
            sys.stdout = original
            log.close()
        else:
            print('- ReadData(): OK: The two data arrays have the same length for file: ' + filename)
    else:
        if logpath:
            original = sys.stdout
            log = open(logpath, 'a')
            sys.stdout = log
            print('- ReadData(): ERROR: The two output data arrays have the same length for file: ' + filename)
            sys.stdout = original
            log.close()
        else:
            print('- ReadData(): ERROR: The two output data arrays have the same length for file: ' + filename)

    return [idata, qdata]

    