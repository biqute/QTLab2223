import checkfile as cf
#nukids_displog missing and necessary to be imported!

def loadconfiguration(filename):
    map = []

    if(cf.checkfile(filename) == False): return None

    fid = open(filename)


    tline = fid.readline()
    while isinstance(tline, str):
        tline = tline.replace(' ', '')
        #[comments] = strread(tline=, '%s %s', 'delimiter','#');

        if tline:
            if(tline[0] != '#'):
                #Remove comments
                [configstr, comments] = tline.split('#')
                [command, value] = configstr.split('=')
                if(not value):
                    dl.DispLog('In config file: "' + filename + '", command "' + command[0] + '" has no value')
                    map = []
                    return map
                if(not command[0]):
                    dl.DispLog('In config file "' + filename + '" value "' + value[0] + '" has no command')
                    map = []
                    return map
                if(command and value):
                    map.append([command, value])

        tline = fid.readline()
    fid.close()
