#!/usr/local/bin/python
# coding=utf-8

import os
import numpy as np
from algorithms.Edmkey.conversions import name_to_class
from matplotlib import pyplot as plt
import librosa.display


def plot_chroma(chromagram):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(chromagram, y_axis='chroma', x_axis='time')
    plt.colorbar()
    plt.title('Chromagram')
    plt.tight_layout()


def euclidean_distance(a, b):
    """
    Returns the euclidean distance between two vectors of equal length.

    """
    return np.linalg.norm(a - b)


def crosscovariance(a, b):
    """
    Calculates the normalized cross-covariance between two vectors.
    Equivalent to the unnormalised crosscorrelation IMHO.

    """
    pass


def crosscorrelation(a, b):
    """
    Calculates a normalized cross-correlation between two vectors.
    Returns the Pearson correlation coefficient.

    """
    from scipy.stats import pearsonr
    return (pearsonr(a, b))[0]


def standard_score(vector):
    """
    Returns a vector normalized to zero mean and unit standard deviation.
    Normally referred to as standardazing.

    La suma del standard score es cero

    """
    return np.divide(np.subtract(vector, np.mean(vector)), np.std(vector))


def unit_vector(vector):
    """ 
    Scale input vectors individually to unit norm (vector length = 1)
    The most commonly encountered vector norm is the L2-norm
    (sometimes called the magnitude of a vector)

     The unit vector obtained by normalizing the normal vector 
     (i.e., dividing a nonzero normal vector by its vector norm)
      is the unit normal vector, often known simply as the "unit normal." 

      Care should be taken to not confuse the terms "vector norm" (length of vector), 
     "normal vector" (perpendicular vector) and "normalized vector" (unit-length vector).

    """
    vector_norm = np.linalg.norm(vector)  # L2-Norm
    if vector_norm == 0:
        return vector
    return vector / vector_norm


def normalize_pcp_area(pcp):
    """
    Normalizes a pcp so that the sum of its content is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.divide(pcp, np.sum(pcp))
    new_format = []
    for item in pcp:
        new_format.append(item)
    return np.array(new_format)


def normalize_pcp_peak(pcp):
    """
    Normalizes a pcp so that the maximum value is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.multiply(pcp, (1 / np.max(pcp)))
    new_format = []
    for item in pcp:
        new_format.append(item)
    return np.array(new_format)


def shift_pcp(pcp, pcp_size=12):
    """
    Shifts a pcp to the nearest tempered bin.
    :type pcp: list
    :type pcp_size: int
    """
    tuning_resolution = pcp_size / 12
    max_val = np.max(pcp)
    if max_val <= [0]:
        max_val = [1]
    pcp = np.divide(pcp, max_val)
    max_val_index = np.where(pcp == 1)
    max_val_index = max_val_index[0] % tuning_resolution
    if max_val_index > (tuning_resolution / 2):
        shift_distance = tuning_resolution - max_val_index
    else:
        shift_distance = max_val_index
    pcp = np.roll(pcp, shift_distance)
    return pcp


def transpose_pcp(pcp, tonic_pc, pcp_size=36):
    """
    Takes an incoming pcp (assuming its first position
    corresponds to the note A and transposes it down so that
    the tonic note corresponds to the first place in the vector.
    """
    transposed = np.roll(pcp, (pcp_size / 12.0) * ((tonic_pc - 9) % 12) * -1)
    return transposed


def extract_median_pcp(dir_estimations, dir_annotations, pcp_size=36):
    """
    Extracts the mean profile from a list of vectors.
    """
    list_estimations = os.listdir(dir_estimations)
    accumulate_profiles = []
    for item in list_estimations:
        if '.key' in item:
            root = open(dir_annotations + '/' + item, 'r')
            root = root.readline()
            root, mode = root[:root.find(' ')], root[root.find(' ') + 1:]
            pcp = open(dir_estimations + '/' + item, 'r')
            pcp = pcp.readline()
            pcp = pcp[pcp.rfind('\t') + 1:].split(', ')
            for i in range(pcp_size):
                pcp[i] = float(pcp[i])
            pcp = transpose_pcp(pcp, name_to_class(root))
            accumulate_profiles.append(pcp)
    return np.median(accumulate_profiles, axis=0)


def pcp_gate(pcp, threshold):
    """
    Zeroes vector elements with values under a certain threshold.
    """
    for i in range(len(pcp)):
        if pcp[i] < threshold:
            pcp[i] = 0
    return pcp


def pcp_sort(pcp):
    """
    Returns a new vector with sorted indexes of the incoming pcp vector.
    """
    pcp = pcp[:]
    idx = []
    for i in range(len(pcp)):
        new_index = pcp.index(np.max(pcp))
        idx.append(new_index)
        pcp[new_index] = -1
    return idx
