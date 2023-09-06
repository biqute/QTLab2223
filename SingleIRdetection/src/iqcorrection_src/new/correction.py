
import numpy as np
import globvar

from datawrapper import LoadSpectraData, FindMixerEllipse, MixerCalibrationData
from utilities import CorrectionLog, Display
from caliq import Cal_IQ, Mixer

home = '/home/alessandro/Lab/Data/'

freq_num = 2
calibration_path = home + 'Calibration/'
mixer_calibration_path = calibration_path + 'MixerCalibration/'
log_path = home + '/Logs/Frequency_' + str(freq_num) + 'Output.log'

# Array of data to be written on the log file
logdata = np.empty((4, ), dtype = int)

# Load spectra from channel data. Note that the output is an array of matrices, each containing data for 1 of the channels
spectra_data, numchannels, num_events, event_length = LoadSpectraData(freq_num)

logdata[0] = numchannels
logdata[1] = num_events
logdata[2] = event_length

# Retrieve the ellipse folder nearest to the working frequency
mixer_calibration_folder = FindMixerEllipse(mixer_calibration_path)
mixer_calibration_data_path = mixer_calibration_path + mixer_calibration_folder + '/'

logdata[3] = mixer_calibration_data_path

# Retrieve ellipse data from the folder we just found
mixer_calibration_data = MixerCalibrationData(mixer_calibration_data_path)

# Store the mixer correction, computed via Cal_IQ function starting from the mixer_calibration_data
mixer = Cal_IQ(mixer_calibration_data)

# Save correction info on log file
CorrectionLog(logdata)



