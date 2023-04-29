import checkfile
import displog
import globalvariables

#nukids_displog missing and necessary to be imported!

def LoadConfiguration(filename):
    map = []

    if(checkfile.CheckFile(filename) == False): 
        return None

    fid = open(filename)
    while True:
        tline = fid.readline()
        tline = tline.replace(' ', '')
        tline = tline.replace('\n', '')
        #[comments] = strread(tline=, '%s %s', 'delimiter','#');

        if not tline: 
            break

        if(tline[0] != '#'):
            #We don't want to read and store comments...
            [command, value] = tline.split('=')
            if(not value):
                displog.DispLog('In config file: "' + filename + '", command "' + command[0] + '" has no value')
                map = []
            if(not command[0]):
                displog.DispLog('In config file "' + filename + '" value "' + value[0] + '" has no command')
                map = []
            if(command and value):
                map.append([command, value])

    fid.close()          
    return map
    
