import sys
import os
import globvar

def DispLog(message):
    
    logpath = globvar.logpath

    if logpath:
        original = sys.stdout
        fid = open(logpath, 'a')
        sys.stdout = fid
        print(message)
        sys.stdout = original
        fid.close()

    else:
        print('- DispLog(): ERROR: Log file not found \n' + message)

