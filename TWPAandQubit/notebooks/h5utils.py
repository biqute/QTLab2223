import h5py
import numpy as np
import matplotlib.pyplot as plt
def descend_obj(obj,sep='\t',index=0):
    """
    Iterate through groups in a HDF5 file and prints the groups and datasets names and datasets attributes
    """

    if type(obj) in [h5py._hl.group.Group,h5py._hl.files.File]:
        #datasets_list = []
        print(sep,'[',index,'] -',obj)
        index = 0
        for key in obj.keys():
            descend_obj(obj[key],sep+'\t',index)
            #if len(datasets_list) == 0:
                #datasets_list = descend_obj(obj[key],sep+'\t',index)
            #else:
                #datasets_list = datasets_list + [descend_obj(obj[key],sep+'\t',index)]
            index = index + 1
    else:
        print(sep,'[',index,']-',obj.name,':',obj.shape)
        #datasets_list = [obj.name]
    #return datasets_list

def h5dump(filename,group='/'):
    """
    print HDF5 file metadata

    group: you can give a specific group, defaults to the root group
    """
    with h5py.File(filename,'r') as f:
         dsets = descend_obj(f[group])
    return dsets

def getDatasets(filename,group="/",shallprint=1):
    """
    Returns a list of all DATASETS in the selected group (not looking into subgroups)
    The list is indexed in the printing order
    """

    # Retrieve list of datasets
    hf = h5py.File(filename, 'r')
    hfg = hf[group]
    children_list = hfg.keys()   # Note: this is a REFERENCE, so closing hf makes "datasets_list" useless!
    datasets = []
    for key in children_list:
        if type(hfg[key]) == h5py._hl.dataset.Dataset:
            datasets = datasets + [key]
    num_sets = len(datasets)
    hf.close()

    # Prints the list in the indexing order
    if shallprint == 1:
        print("Datasets in ", group,":\n")
        for i in np.arange(0,num_sets):
            print("[" + str(i) + "]" + " " + datasets[i] + "\n")
    return datasets

def getGroups(filename,group="/",shallprint=1):
    """
    Returns a list of all GROUPS in the selected group (not looking into subgroups)
    The list is indexed in the printing order
    """

    # Retrieve list of datasets
    hf = h5py.File(filename, 'r')
    hfg = hf[group]
    children_list = hf.keys()   # Note: this is a REFERENCE, so closing hf makes "datasets_list" useless!
    groups = []
    for key in children_list:
        if type(hfg[key]) == h5py._hl.group.Group:
            groups = groups + [key]
    num_groups = len(groups)
    hf.close()

    # Prints the list in the indexing order
    if shallprint == 1:
        print("Groups in ", group,":\n")
        for i in np.arange(0,num_groups):
            print("[" + str(i) + "]" + " " + groups[i] + "\n")
    return groups

def plotDataset(filename, group="/", dataset_index = 0, xmin = float('-inf'), xmax = float('inf'), rescale_xaxis = 1, xlabel = "x", ylabel = "y", groupoff = "", fitline = False, calc_ave = False, plot_phase = 0):
    """
    Plot the specified dataset from the specified group.
    """

    # Retrieve data from the specified dataset
    datasets = getDatasets(filename,group,0)
    hf = h5py.File(filename, 'r')
    hfg = hf[group]
    dataset_mat = hfg.get(datasets[dataset_index])
    size_dataset = len(dataset_mat)
    xs = dataset_mat[0]
    num = len(xs)
    ys = np.zeros(num)
    I = np.zeros(num)
    Q = np.zeros(num)
    if size_dataset == 2:
        ys = dataset_mat[1]
    else:
        I = dataset_mat[1]
        Q = dataset_mat[2]
    hf.close()  # Note: dataset_mat is just a reference, so hf file must be close AFTER assigning freq and S21dBm!
    
    # Retrieve Off data (if required)
    if groupoff != "":
        datasets = getDatasets(filename,groupoff,0)
        hf = h5py.File(filename, 'r')
        hfg = hf[groupoff]
        dataset_mat = hfg.get(datasets[dataset_index])    
        if size_dataset == 2:
            ysoff = dataset_mat[1]
            ys = ys - ysoff # Remove Off measure
        else:
            Ioff = dataset_mat[1]
            Qoff = dataset_mat[2]
            I = I - Ioff
            Q = Q - Qoff
        num = len(xs)
        hf.close()

    # If Dataset contains I,Q you can choose between phase or modulus
    if size_dataset == 3:
        S21dB = 20*np.log10(np.sqrt(np.multiply(I,I)+np.multiply(Q,Q)))
        phase = np.arctan2(I,Q)
        if plot_phase == 0:
            ys = S21dB
        else:
            ys = phase
    # Plot
    fig, ax = plt.subplots()
    i_min = max(round((xmin-xs[0])/((xs[num-1]-xs[0])/num)),0)
    i_max = min(round((xmax-xs[0])/((xs[num-1]-xs[0])/num)),num-1)
    i_min = min(i_min, num - 1)
    i_max = max(i_max, 0)
    if i_min >= i_max:
        i_min = 0
        i_max = num - 1
        xmin = xs[i_min]
        xmax = xs[i_max]
        print("Invalid frequency span; Select\nxmin > ",xs[0]/rescale_xaxis," x ",rescale_xaxis,"\nxmax <",xs[num-1]/rescale_xaxis," x ",rescale_xaxis,"\n")
    
    ax.plot(xs[i_min:i_max]/rescale_xaxis, ys[i_min:i_max], label = str(datasets[dataset_index]))

    # Fit (if required)
    if fitline == True:
        p, res, _, _, _ = np.polyfit(xs[i_min:i_max]/1e9,ys[i_min:i_max],1,full=True)
        ax.plot(xs[i_min:i_max]/1e9,p[1]+p[0]*xs[i_min:i_max]/1e9, label = "Slope: " + str(round(p[0],3)) + " dBm/Ghz")

    # Calculate Band Ave+-Std and put it in title (if required)
    if calc_ave == True:
        ave = np.mean(ys[i_min:i_max])
        std = np.std(ys[i_min:i_max])
    # Generate title
    title = "Number of Points: " + str(i_max - i_min + 1)
    if calc_ave == True:
        title = title + "\nBand Average ["+ str(round(xmin/rescale_xaxis,3)) +", " + str(round(xmax/rescale_xaxis,3)) + "]GHz: "
        title = title +  str(round(ave,3)) + "+-" + str(round(std,3)) + " dBm"
    ax.set_title(title)


    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.legend()
    plt.show()

    return fig, ax

def plotDatasetSpectrum(filename, group="/", dataset_index = 0, fmin = float('-inf'), fmax = float('inf'), rescale_xaxis = 1e9, groupoff = "", fitline = False, calc_ave = False, plot_phase = 0):
    """
    Plot the specified dataset from the specified group,
    ASSUMING its a spectrum (S21 [dBm] vs. frequency [GHz])
    """
    if plot_phase == 0:
        ylabel = "$|S_{21}|} [dB]$"
    else:
        ylabel = "Phase [rad]"
    return plotDataset(filename,group,dataset_index,fmin,fmax,rescale_xaxis,"frequency [GHz]",ylabel, groupoff = groupoff, fitline = fitline, calc_ave = calc_ave, plot_phase = 0)

def plotAllDatasets(filename, group="/", rescale_xaxis = 1, xlabel = "x", ylabel = "y", plot_phase = 0):
    """
    Plot ALL datasets from the specified group (not into the subgroups!)
    """

    # Retrieve data from the specified dataset
    datasets = getDatasets(filename,group,0)
    num_sets = len(datasets)
    hf = h5py.File(filename, 'r')
    hfg = hf[group]

    # Plot
    fig, ax = plt.subplots()
    for i in np.arange(0, num_sets):    #Warning: Through the cycle the "hf" file is kept OPEN!
        dataset_mat = hfg.get(datasets[i])
        xs = dataset_mat[0]
        if len(dataset_mat) == 2:
            ys = dataset_mat[1]
        else:
            I = dataset_mat[1]
            Q = dataset_mat[2]
            S21dB = 20*np.log10(np.sqrt(np.multiply(I,I)+np.multiply(Q,Q)))
            phase = np.arctan2(I,Q)
            if plot_phase == 0:
                ys = S21dB
            else:
                ys = phase
        ax.plot(xs/rescale_xaxis, ys, label = str(datasets[i]))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.legend()

    #plt.show()
    hf.close()

    return fig, ax

def plotAllDatasetsSpectrum(filename, group = "/", rescale_xaxis = 1e9, plot_phase = 0):
    return plotAllDatasets(filename,group,rescale_xaxis,"frequency [GHz]","$S_{21}$ [dBm]", plot_phase = plot_phase)

def getDatasetValue(filename,group,dataset_index):
    datasets = getDatasets(filename,group,0)
    hf = h5py.File(filename, 'r')
    hfg = hf[group]
    dataset_mat = hfg.get(datasets[dataset_index])
    xs = dataset_mat[0]
    ys = dataset_mat[1]
    zs = np.zeros(len(xs))
    if len(dataset_mat) == 3:
        zs = dataset_mat[2]
    hf.close()

    if len(dataset_mat) < 3:
        return xs, ys
    elif len(dataset_mat) == 3:
        return xs, ys
    else:
        return 0    # Error


def deleteDataset(filename, full_dataset_path = "/to/delete/path/dataset"):
    """
    DELETE the specified dataset
    """
    # "full_dataset_path" e.g. group/datasetname    #NOTe: Name included!!!
    with h5py.File(filename,  "a") as f:
        del f[full_dataset_path]

def fspan_to_ispan(vec,fmin,fmax):
    """
    fmin, fmax -> i_min, i_max
    """
    i_min = max(round((fmin-vec[0])/((vec[len(vec)-1]-vec[0])/len(vec))),0)
    i_max = min(round((fmax-vec[0])/((vec[len(vec)-1]-vec[0])/len(vec))),len(vec)-1)
    i_min = min(i_min, len(vec) - 1)  # If fmin, fmax are out of measurement span, take the measurement span
    i_max = max(i_max, 0)

    return i_min, i_max