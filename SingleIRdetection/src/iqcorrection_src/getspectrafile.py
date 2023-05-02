import os
import sys
import numpy as np
import globvar

def GetSpectraFile(key):

    logpath = globvar.logpath
    out = []
    original = sys.stdout

    #list is indeed a list of all directories in "key" path which begin with the character specified
    #default is set to any character
    list = os.listdir(key)
    #list = [f for f in list if f.startswith('.')]

    i = 0
    k = 0
    nonnull = 0
    temp = (['null']*len(list))

    for i in range(len(list)):
        #if((list[i].find('.hdr') == -1) and (list[i].find('time') == -1) and (list[i].find('.log') == -1)):  #(?)
        if((list[i].find('.hdr') == -1) and (list[i].find('.log') == -1) and (list[i].find('spectra') == -1)):
            temp[i-k] = list[i]
            nonnull = nonnull + 1
        else:
            k=k+1
        
    for jj in range(len(temp)):
        if temp[jj] != 'null':
            out.append(temp[jj])


    if logpath:
        log = open(logpath, 'a')
        sys.stdout = log  
        
        if (('out' in locals()) or ('out' in globals())):
            print('- GetSpectraFile(): OK spectra files found: ' + str(key) +'\n')
        
        else:
            print('- GetSpectraFile(): ERROR no spectra files found: ' + str(key) + '\n')
            out=[]

        log.close()

    sys.stdout = original

    return out