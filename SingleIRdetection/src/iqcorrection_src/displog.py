import sys
import os
from globalvariables import logpath

def DispLog(message):
    
    if logpath:
        original = sys.stdout
        fid = open(logpath, 'a')
        sys.stdout = fid
        print(message)
        sys.stdout = original
        fid.close()


