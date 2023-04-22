import sys

def CompareVector(a, b):
    global logpath

    if logpath:
        fid = open(logpath, 'a')
        original_stdout = sys.stdout
        sys.stdout = fid
        if len(a) == len(b):
            print('CompareVector(): OK: the two frequency vectors have the same length: ' + str(len(a)))
            for i in range(len(a)):
                if abs((a[i]/b[i] - 1)) > 0.000001:
                    print('CompareVector(): ERROR: different frequencies at position ' + str(i) + '| first frequency: ' + str(a[i]) + '| second frequency: ' + str(b[i]))
                    return
                
        else:
            sys.stdout = original_stdout
            fid.close()
    
    else:
        if len(a) == len(b):

            for i in range(len(a)):
                if abs((a[i]/b[i] - 1)) > 0.000001:
                    print('CompareVector(): ERROR: different frequencies at position ' + str(i) + '| first frequency: ' + str(a[i]) + '| second frequency: ' + str(b[i]))

                    return
        
        else:
            print('CompareVector(): ERROR: the two vectors have different lentghs : '+ str(len(a)) + ' and: ' + str(len(b)))
        

        