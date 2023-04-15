import os

def GetSpectraFile(key):

    global logpath
    out = []

    #list is indeed a list of all directories in "key" path which begin with the character specified
    #default is set to any character
    list = os.listdir(key)
    #list = [f for f in list if f.startswith('.')]
    list = str(list)

    k = 0
    out = ([[]]*len(list))

    for i in range(len(list)):
        if((list[i].find('.hdr') == -1) and (list[i].find('time') == -1) and (list[i].find('.log') == -1)):
            out[i-k] = list[i]
        else:
            k=k+1

    print(list)

    if logpath:
           
        if (('out' in locals()) or ('out' in globals())):
            log = open(logpath, 'a+')
            print(str(log) + 'get_spectra_file() OK spectra files found: ' + str(key) +'\n')
            log.close()
        
        else:
            log = open(logpath, 'a+')
            print(str(log) + 'get_spectra_file() ERROR no spectra files found: ' + str(key) + '\n')
            log.close()
            out=[]

    return out