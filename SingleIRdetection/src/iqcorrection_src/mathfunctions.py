import numpy as np

def MaxColumnWise(matrix):
    max_val = np.amax(matrix, axis = 0)
    max_pos = np.argmax(matrix, axis = 0)
    return [max_val, max_pos]

def MinColumnWise(matrix):
    min_val = np.amin(matrix, axis = 0)
    min_pos = np.argmin(matrix, axis = 0)
    return [min_val, min_pos]
