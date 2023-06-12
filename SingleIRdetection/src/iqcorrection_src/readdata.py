import numpy as np
import globvar
from displog import DispLog
import sys

def ReadData(filename, icol, qcol, start = 0, stop = 'none'):
    #start is the starting row
    #stop is the final row
    #ReadData translates into a matrix everything between these two rows
    if stop != 'none':
        rows = stop - start
        if rows > 1:
            data = np.loadtxt(filename, dtype = float, delimiter = '\t', skiprows = start, max_rows = rows)
        else:
            DispLog('- ReadData(): ERROR: Number of rows is 1, maybe you typed something wrong!')
            return
    else:
        data = np.loadtxt(filename, dtype = float, delimiter = '\t', skiprows = start)

    datapoints = data.shape[0]

    if datapoints < globvar.recordlength:
        DispLog('- ReadData(): WARNING: The number of points from the setup file is greater than the actual record length for file: ' + filename)

    idata = np.array(data[:, icol])
    qdata = np.array(data[:, qcol])

    if (len(idata) == len(qdata)):
        DispLog('- ReadData(): OK: The two data arrays have the same length for file: ' + filename)

    return [idata, qdata]

    