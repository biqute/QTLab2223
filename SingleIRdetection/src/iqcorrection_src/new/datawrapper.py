import os
import numpy as np
import re
import h5py

from utilities import NumbersInString

def DatasetCounter(group):
    count = 0
    for key in group.keys():
        if isinstance(group, h5py.Dataset):
            count += 1
    return count

def DataFiles(data_path):
    if data_path[-1] != '/':
        data_path = data_path + '/'
    data_files = []
    files = os.listdir(data_path)
    for file in files:
        if (file.find('.csv') != -1 and file.find('lock') == -1):
            data_files.append(data_path + file)
    data_files.sort(key = lambda f: (re.sub('\D', '', f)))
    return data_files

def LoadData(data_file, skip = 21, delim = ','):
    data = np.loadtxt(data_file, skiprows = skip, delimiter = delim)
    return data

def DeleteInfs(data):
    positions = np.where(data == np.inf)
    rows = np.sort(np.array(positions[0]))
    columns = np.sort(np.array(positions[1]))
    for i in range(len(rows)):
        if (rows[i] > 0 and rows[i] != data.shape[0]):
            data[rows[i], columns[i]] = (data[rows[i] + 1, columns[i]] + data[rows[i] - 1, columns[i]])/2
        elif (rows[i] == data.shape[0] - 1):
            data[rows[i], columns[i]] = data[rows[i] - 1, columns[i]]   
        elif (rows[i] == 0):
            data[rows[i], columns[i]] = data[rows[i] + 1, columns[i]]
    return data

def RunBuild(data_path, verbosity = 0, eventlength = 2500):

    data_files = DataFiles(data_path)
    numfiles = len(data_files)
    data = LoadData(data_files[0])
    recordlength0 = data.shape[0]
    recordlength = data.shape[0]
    for data_file in data_files[1:-1]:
        temp_data = LoadData(data_file)
        data = np.vstack([data, temp_data])
        recordlength += data.shape[0]
    data = DeleteInfs(data)

    # We want to store data coherently with the .watson format
    recordlength = data.shape[0]
    numchannels = data.shape[1]
    totevents = int(recordlength / (eventlength))

    #Setup a coherent dataset. Eventually discard the last event (?could this be improved?)
    data = data[0: totevents*eventlength, :]

    #Array of ndarrays to store data for every channel
    channels = np.empty((numchannels, ), dtype = np.ndarray)
    for ch in range(numchannels):
        current_channel = data[:, ch]
        matrix = current_channel.reshape(totevents, eventlength)
        channels[ch] = matrix        

    if verbosity == 1:
        print(' --> RunBuild: Built ' + data_path[-4:])

    return channels

def RunsBuild(runs_path, verb = 1, evelength = 2500):
    if runs_path[-1] != '/':
            runs_path = runs_path + '/'    
    
    search_name = 'Frequency'
    name_index = runs_path.find(search_name)
    frequency_name = runs_path[name_index: name_index + len(search_name) + 7]

    runs = []
    list = os.listdir(runs_path)
    for file in list:
        if (file.find('run') != -1):
            runs.append(runs_path + file)
    
    channels = RunBuild(runs[0], verbosity = verb, eventlength = evelength)

    nchan = len(channels)
    for run in runs[1: ]:
        current_channels = RunBuild(run, verbosity = verb, eventlength = evelength)
        for ch in range(nchan):
            channels[ch] = np.vstack([channels[ch], current_channels[ch]])
        if verb == 1:
            print(' --> RunsBuild: Dimensions check || Matrices for ' + run[-4:] + ' have dimensions \n')
            for ch in range(nchan):
                print(' --> RunsBuild: Channel ' + str(ch + 1) + '[' + str(channels[ch].shape[0]) + '] x [' + str(channels[ch].shape[1]) + '] \n' )
            print(' --> RunsBuild: ' + run[-4:] + ' material attached')

    hf = h5py.File(runs_path + 'Assembled', 'w')
    hfdat = hf.create_group(frequency_name)
    for ch in range(nchan):
        hfdat.create_dataset('Channel ' + str(ch), (channels[ch].shape[0], channels[ch].shape[1]), data = channels[ch])
    
    hf.close()
    return

#------------------------------Calibration and Mixer Correction-----------------------------------

def Frequency(freq_num):
    '''This simply translates the frequency number into the actual frequency value'''
    frequencies = np.array([5.35, 5.58, 5.67, 5.98])
    return frequencies[freq_num - 1]

def LoadSpectraData(freq_num, freq_path = '/home/alessandro/Lab/Data/Frequency_'):
    assembled_path = freq_path + str(freq_num) + '_35mK/Resonance/Assembled'
    hf = h5py.File(assembled_path, 'r')
    channels_group = hf['Frequency_' + str(freq_num) + '_35mK']
    numchannels = DatasetCounter(channels_group)
    data = np.empty((numchannels, ), dtype = np.ndarray)
    for ch in range(numchannels):
        data[ch] = channels_group['Channel ' + str(ch)][:]

        # This check is just to make the computation once. Number of events and event length are the same for each channel
        if ch == 0:
            event_length = data[ch].shape[1]
            num_events = data[ch].shape[0]

    hf.close()

    return data, int(numchannels), int(num_events), int(event_length)

def FindMixerEllipse(freq_num, mixer_calibration_path):
    '''This function finds the ellipse data folder at the frequency nearest to the input value'''
    freq = Frequency(freq_num)
    calibration_folders = os.listdir(mixer_calibration_path)
    min = 1
    for folder in calibration_folders:
        freq_ranges = NumbersInString(folder)
        interval = freq_ranges[1] - freq_ranges[0]
        avg = (freq_ranges[1] + freq_ranges[0])/2
        if interval >= 0.003:
            diff = freq - avg
            if diff < min:
                min = diff
                calibration_folder = folder
    return calibration_folder

def MixerCalibrationData(mixer_calibration_data_path):
    '''Returns a matrix containing data for the IQ - Mixer ellipse'''

    prefix = 'IQmixercal_'
    fname = prefix + '0.txt'
    Iname = prefix + '1.txt'
    Qname = prefix + '2.txt'
    f = np.loadtxt(mixer_calibration_data_path + 'run1/' + fname)
    I = np.loadtxt(mixer_calibration_data_path + 'run1/' + Iname)
    Q = np.loadtxt(mixer_calibration_data_path + 'run1/' + Qname)

    data = np.column_stack([I, Q])
    f = np.array(f)
    return f, data
    
    


    