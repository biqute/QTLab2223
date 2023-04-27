import os
#This function does exactly what the name suggests: it checks if a given path exists.
#If the path does not exists it displays a negative result in the log file.


def CheckFile(filename):
    if not os.path.exists(filename):
        print('File: ' + filename + ' does not exist')
        valid = False
    else:
        valid = True
    
    return valid