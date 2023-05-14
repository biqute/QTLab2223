import numpy as np

def ReadData(filename, ncol, icol, qcol, start, npoints):

    ncol = int(ncol)
    npoints = int(npoints)

    data = np.loadtxt(filename, dtype = float, delimiter = '\t')

    start = start

    idata = np.array(data[:, icol])
    qdata = np.array(data[:, qcol])

    return idata, qdata

    