import globvar
import numpy as np

def ReadBinaryData(filename, ncol, xcol, ycol, start, npoints):
    #Reads the labview binary format data
    #
    #Usage:  [Idata, Qdata] = readbinarydata( filename, start, npoints)
    #inputs:
    #   filename -      name of file
    #   ncol -          total number of columns
    #   xcol -          column for I data
    #   ycol -          column for Q data
    #   start -         first point to read, 0 for start of file
    #   npoints -       number of points to read, inf for complete file
    #outputs
    #   Idata -         I quadrature data
    #   Qdata -         Q

    dataformat = globvar.dataformat
    ncol = int(ncol)
    npoints = int(npoints)
    fid = open(filename)

    if start > 0:
        data = np.array(np.fromfile(fid, dtype = '>i2'))
        data = data.reshape([ncol, npoints])
    
    data = np.fromfile(fid, dtype = '>i2')
    data = data.reshape([ncol, npoints])

    idata = data[xcol, 9:-1]
    idata = idata[:]
    qdata = data[ycol, 9:-1]
    qdata = qdata[:]

    return [idata, qdata]

    