global adcconv
global checkpath
global dataformat
global logpath
global recordlength

spectra_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Data\\Spectra'
run_num = 34
datatype = 'MixCh'
meas_num = 1
save_path = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\Save'
iqpath = '\\Users\\alexb\\OneDrive\\Documenti\\Lab_locale\\iqcorrection\\iqcorrection_src\\IQ'
iqheader = ['IQ0Ch1off', 'IQ0Ch2off']
nch = 2
mode = 0

logpath = logpath = save_path + '\\run' + str(run_num) + '\\' + datatype + str(meas_num) +'.log'