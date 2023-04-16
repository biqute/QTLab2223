import os

def checkfile(filename):
    if os.path.exists(filename):
        print('File: ' + filename + ' does not exist')
        valid = False
    else:
        valid = True
    
    return valid