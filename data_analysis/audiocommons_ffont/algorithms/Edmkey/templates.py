# coding=utf-8
import numpy as np
from scipy.stats import pearsonr

# Essentia's algorithm had a function to resize pcp's to fit the key profiles
# consider implementing this in the future

# podríamos generar perfiles que, una vez extraídas sus características modales,
# maximicen la diferencia entre ellos

# it is going to be sensible as to whether we start counting on A or on C... I would suggest C, thoguh
key_names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"] # ELSE
# key_names = ["A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab"] # ESSENTIA


def template_matching_2(pcp, profile_type='bgate'):

    key_templates = {

    'bgate': np.array([[1., 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.77, 0.00, 0.38, 0.21, 0.30],
                       [1., 0.00, 0.36, 0.39, 0.00, 0.38, 0.00, 0.74, 0.27, 0.00, 0.42, 0.23]]),

    # almost identical to bgate. kept for backwards compatibility
    'bmtg3': np.array([[1.00, 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.76, 0.00, 0.38, 0.21, 0.30],
                       [1.00, 0.00, 0.36, 0.39, 0.10, 0.37, 0.00, 0.76, 0.27, 0.00, 0.42, 0.23]]),

    'bmtg2': np.array([[1.00, 0.10, 0.42, 0.10, 0.53, 0.37, 0.10, 0.77, 0.10, 0.38, 0.21, 0.30],
                       [1.00, 0.10, 0.36, 0.39, 0.29, 0.38, 0.10, 0.74, 0.27, 0.10, 0.42, 0.23]]),

    # was originally bmtg1
    'braw': np.array([[1., 0.1573, 0.4200, 0.1570, 0.5296, 0.3669, 0.1632, 0.7711, 0.1676, 0.3827, 0.2113, 0.2965],
                      [1., 0.2330, 0.3615, 0.3905, 0.2925, 0.3777, 0.1961, 0.7425, 0.2701, 0.2161, 0.4228, 0.2272]]),

    'diatonic': np.array([[1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]]),

    'monotonic': np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]),

    'triads': np.array([[1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                        [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]]),

    'edma_ecir': np.array([[0.16519551, 0.04749026, 0.08293076, 0.06687112, 0.09994645, 0.09274123, 0.05294487, 0.13159476, 0.05218986, 0.07443653, 0.06940723, 0.0642515],
                           [0.17235348, 0.05336489, 0.0761009, 0.10043649, 0.05621498, 0.08527853, 0.0497915, 0.13451001, 0.07458916, 0.05003023, 0.09187879, 0.05545106]]),

    'edmm_ecir': np.array([[0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083, 0.083],
                           [0.17235348, 0.04, 0.0761009, 0.12, 0.05621498, 0.08527853, 0.0497915, 0.13451001, 0.07458916, 0.05003023, 0.09187879, 0.05545106]]),

    'edma':  np.array([[1., 0.2875, 0.5020, 0.4048, 0.6050, 0.5614, 0.3205, 0.7966, 0.3159, 0.4506, 0.4202, 0.3889],
                       [1., 0.3096, 0.4415, 0.5827, 0.3262, 0.4948, 0.2889, 0.7804, 0.4328, 0.2903, 0.5331, 0.3217]]),

    'edmm':  np.array([[1., 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000],
                       [1., 0.2321, 0.4415, 0.6962, 0.3262, 0.4948, 0.2889, 0.7804, 0.4328, 0.2903, 0.5331, 0.3217]]),

    'krumhansl': np.array([[6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
                           [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]]),

    'temperley99': np.array([[5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0],
                             [5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0]]),

    'temperley05': np.array([[0.748, 0.060, 0.488, 0.082, 0.67, 0.46, 0.096, 0.715, 0.104, 0.366, 0.057, 0.4],
                             [0.712, 0.084, 0.474, 0.618, 0.049, 0.46, 0.105, 0.747, 0.404, 0.067, 0.133, 0.33]]),

    'temperley-essen': np.array([[0.184, 0.001, 0.155, 0.003, 0.191, 0.109, 0.005, 0.214, 0.001, 0.078, 0.004, 0.055],
                                 [0.192, 0.005, 0.149, 0.179, 0.002, 0.144, 0.002, 0.201, 0.038, 0.012, 0.053, 0.022]]),

    'thpcp': np.array([[0.95162, 0.20742, 0.71758, 0.22007, 0.71341, 0.48841, 0.31431, 1.00000, 0.20957, 0.53657, 0.22585, 0.55363],
                       [0.94409, 0.21742, 0.64525, 0.63229, 0.27897, 0.57709, 0.26428, 1.0000, 0.26428, 0.30633, 0.45924, 0.35929]]),

    'shaath': np.array([[6.6, 2.0, 3.5, 2.3, 4.6, 4.0, 2.5, 5.2, 2.4, 3.7, 2.3, 3.4],
                        [6.5, 2.7, 3.5, 5.4, 2.6, 3.5, 2.5, 5.2, 4.0, 2.7, 4.3, 3.2]]),

    'gomez': np.array([[0.82, 0.00, 0.55, 0.00, 0.53, 0.30, 0.08, 1.00, 0.00, 0.38, 0.00, 0.47],
                       [0.81, 0.00, 0.53, 0.54, 0.00, 0.27, 0.07, 1.00, 0.27, 0.07, 0.10, 0.36]]),

    'faraldo': np.array([[7.0, 2.0, 3.8, 2.3, 4.7, 4.1, 2.5, 5.2, 2.0, 3.7, 3.0, 3.4],
                         [7.0, 3.0, 3.8, 4.5, 2.6, 3.5, 2.5, 5.2, 4.0, 2.5, 4.5, 3.0]]),

    'pentatonic': np.array([[1.0, 0.1, 0.25, 0.1, 0.5, 0.7, 0.1, 0.8, 0.1, 0.25, 0.1, 0.5],
                            [1.0, 0.2, 0.25, 0.5, 0.1, 0.7, 0.1, 0.8, 0.3, 0.2, 0.6, 0.2]]),

    'noland': np.array([[0.0629, 0.0146, 0.061, 0.0121, 0.0623, 0.0414, 0.0248, 0.0631, 0.015, 0.0521, 0.0142, 0.0478],
                        [0.0682, 0.0138, 0.0543, 0.0519, 0.0234, 0.0544, 0.0176, 0.067, 0.0349, 0.0297, 0.0401, 0.027]])
    }

    if (pcp.size < 12) or (pcp.size % 12 != 0):
        raise IndexError("Input PCP size is not a positive multiple of 12")

    _major, _minor = _select_profile_type(profile_type, key_templates)

    first_max_major = -1
    second_max_major = -1
    key_index_major = -1

    first_max_minor = -1
    second_max_minor = -1
    key_index_minor = -1

    for shift in np.arange(pcp.size):
        correlation_major = (pearsonr(pcp, np.roll(_major, shift)))[0]
        if correlation_major > first_max_major:
            second_max_major = first_max_major
            first_max_major = correlation_major
            key_index_major = shift

        correlation_minor = (pearsonr(pcp, np.roll(_minor, shift)))[0]
        if correlation_minor > first_max_minor:
            second_max_minor = first_max_minor
            first_max_minor = correlation_minor
            key_index_minor = shift

    if first_max_major > first_max_minor:
        key_index = key_index_major
        scale = 'major'
        first_max = first_max_major
        second_max = second_max_major
    elif first_max_minor > first_max_major:
        key_index = key_index_minor
        scale = 'minor'
        first_max = first_max_minor
        second_max = second_max_minor
    else:
        key_index = -1
        first_max = -1
        second_max = -1
        scale = 'unknown'

    if key_index < 0:
        raise IndexError("key_index smaller than zero. Could not find key.")
    else:
        first_to_second_ratio = (first_max - second_max) / first_max
        return key_names[int(key_index)], scale, first_max, first_to_second_ratio


def template_matching_3(pcp, profile_type='bgate'):
    if (pcp.size < 12) or (pcp.size % 12 != 0):
        raise IndexError("Input PCP size is not a positive multiple of 12")

    key_templates = {

    'bgate': np.array([[1., 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.77, 0.00, 0.38, 0.21, 0.30],
                       [1., 0.00, 0.36, 0.39, 0.00, 0.38, 0.00, 0.74, 0.27, 0.00, 0.42, 0.23],
                       [1., 0.26, 0.35, 0.29, 0.44, 0.36, 0.21, 0.78, 0.26, 0.25, 0.32, 0.26]]),

    # almost identical to bgate, predecessor.
    'bmtg3': np.array([[1., 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.76, 0.00, 0.38, 0.21, 0.30],
                       [1., 0.00, 0.36, 0.39, 0.10, 0.37, 0.00, 0.76, 0.27, 0.00, 0.42, 0.23],
                       [1., 0.26, 0.35, 0.29, 0.44, 0.37, 0.21, 0.76, 0.26, 0.25, 0.32, 0.26]]),

    'bmtg2': np.array([[1., 0.10, 0.42, 0.10, 0.53, 0.37, 0.10, 0.77, 0.10, 0.38, 0.21, 0.30],
                       [1., 0.10, 0.36, 0.39, 0.29, 0.38, 0.10, 0.74, 0.27, 0.10, 0.42, 0.23],
                       [1., 0.26, 0.35, 0.29, 0.44, 0.36, 0.21, 0.78, 0.26, 0.25, 0.32, 0.26]]),

    # was bmtg1
    'braw':  np.array([[1., 0.1573, 0.4200, 0.1570, 0.5296, 0.3669, 0.1632, 0.7711, 0.1676, 0.3827, 0.2113, 0.2965],
                       [1., 0.2330, 0.3615, 0.3905, 0.2925, 0.3777, 0.1961, 0.7425, 0.2701, 0.2161, 0.4228, 0.2272],
                       [1., 0.2608, 0.3528, 0.2935, 0.4393, 0.3580, 0.2137, 0.7809, 0.2578, 0.2539, 0.3233, 0.2615]]),

    'edma':  np.array([[1.00, 0.29, 0.50, 0.40, 0.60, 0.56, 0.32, 0.80, 0.31, 0.45, 0.42, 0.39],
                       [1.00, 0.31, 0.44, 0.58, 0.33, 0.49, 0.29, 0.78, 0.43, 0.29, 0.53, 0.32],
                       [1.00, 0.26, 0.35, 0.29, 0.44, 0.36, 0.21, 0.78, 0.26, 0.25, 0.32, 0.26]])
    }

    _major, _minor, _minor2 = _select_profile_type(profile_type, key_templates)

    first_max_major   = -1
    second_max_major  = -1
    key_index_major   = -1

    first_max_minor   = -1
    second_max_minor  = -1
    key_index_minor   = -1

    first_max_minor2  = -1
    second_max_minor2 = -1
    key_index_minor2  = -1

    for shift in np.arange(pcp.size):
        correlation_major = (pearsonr(pcp, np.roll(_major, shift)))[0]
        if correlation_major > first_max_major:
            second_max_major = first_max_major
            first_max_major = correlation_major
            key_index_major = shift

        correlation_minor = (pearsonr(pcp, np.roll(_minor, shift)))[0]
        if correlation_minor > first_max_minor:
            second_max_minor = first_max_minor
            first_max_minor = correlation_minor
            key_index_minor = shift

        correlation_minor2 = (pearsonr(pcp, np.roll(_minor2, shift)))[0]
        if correlation_minor2 > first_max_minor2:
            second_max_minor2 = first_max_minor2
            first_max_minor2 = correlation_minor2
            key_index_minor2 = shift

    if (first_max_major > first_max_minor) and (first_max_major > first_max_minor2):
        key_index = key_index_major
        scale = 'major'
        first_max = first_max_major
        second_max = second_max_major

    elif (first_max_minor >= first_max_major) and (first_max_minor >= first_max_minor2):
        key_index = key_index_minor
        scale = 'minor'
        first_max = first_max_minor
        second_max = second_max_minor

    elif (first_max_minor2 > first_max_major) and (first_max_minor2 > first_max_minor):
        key_index = key_index_minor2
        scale = 'minor'
        first_max = first_max_minor2
        second_max = second_max_minor2

    else:
        key_index = -1
        first_max = -1
        second_max = -1
        scale = 'unknown'

    if key_index < 0:
        raise IndexError("key_index smaller than zero. Could not find key.")
    else:
        first_to_second_ratio = (first_max - second_max) / first_max
        return key_names[int(key_index)], scale, first_max, first_to_second_ratio


def template_matching_modal(pcp):
    if (pcp.size < 12) or (pcp.size % 12 != 0):
        raise IndexError("Input PCP size is not a positive multiple of 12")

    key_templates = {

        'ionian': np.array([1.00, 0.10, 0.43, 0.14, 0.61, 0.38, 0.12, 0.78, 0.13, 0.46, 0.15, 0.60]),

        'harmonic': np.array([1.00, 0.10, 0.36, 0.37, 0.22, 0.33, 0.18, 0.75, 0.25, 0.18, 0.37, 0.37]),

        'mixolydian': np.array([1.00, 0.10, 0.42, 0.10, 0.55, 0.40, 0.10, 0.77, 0.10, 0.42, 0.66, 0.15]),

        'phrygian': np.array([1.00, 0.47, 0.10, 0.36, 0.24, 0.37, 0.16, 0.76, 0.30, 0.20, 0.45, 0.23]),

        'fifth': np.array([1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.65, 0.00, 0.00, 0.00, 0.00]),

        'monotonic': np.array([1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]),

        'difficult': np.array([0.80, 0.60, 0.80, 0.60, 0.80, 0.60, 0.80, 0.60, 0.80, 0.60, 0.80, 0.60]),

    }

    first_max_ionian      = -1
    second_max_ionian     = -1
    key_index_ionian      = -1

    first_max_harmonic    = -1
    second_max_harmonic   = -1
    key_index_harmonic    = -1

    first_max_mixolydian  = -1
    second_max_mixolydian = -1
    key_index_mixolydian  = -1

    first_max_phrygian    = -1
    second_max_phrygian   = -1
    key_index_phrygian    = -1

    first_max_fifth       = -1
    second_max_fifth      = -1
    key_index_fifth       = -1

    first_max_monotonic   = -1
    second_max_monotonic  = -1
    key_index_monotonic   = -1

    first_max_difficult   = -1
    second_max_difficult  = -1
    key_index_difficult   = -1

    for shift in np.arange(pcp.size):
        correlation_ionian = (pearsonr(pcp, np.roll(key_templates['ionian'], shift)))[0]
        if correlation_ionian > first_max_ionian:
            second_max_ionian = first_max_ionian
            first_max_ionian = correlation_ionian
            key_index_ionian = shift

        correlation_harmonic = (pearsonr(pcp, np.roll(key_templates['harmonic'], shift)))[0]
        if correlation_harmonic > first_max_harmonic:
            second_max_harmonic = first_max_harmonic
            first_max_harmonic = correlation_harmonic
            key_index_harmonic = shift

        correlation_mixolydian = (pearsonr(pcp, np.roll(key_templates['mixolydian'], shift)))[0]
        if correlation_mixolydian > first_max_mixolydian:
            second_max_mixolydian = first_max_mixolydian
            first_max_mixolydian = correlation_mixolydian
            key_index_mixolydian = shift

        correlation_phrygian = (pearsonr(pcp, np.roll(key_templates['phrygian'], shift)))[0]
        if correlation_phrygian > first_max_phrygian:
            second_max_phrygian = first_max_phrygian
            first_max_phrygian = correlation_phrygian
            key_index_phrygian = shift

        correlation_fifth = (pearsonr(pcp, np.roll(key_templates['fifth'], shift)))[0]
        if correlation_fifth > first_max_fifth:
            second_max_fifth = first_max_fifth
            first_max_fifth = correlation_fifth
            key_index_fifth = shift

        correlation_monotonic = (pearsonr(pcp, np.roll(key_templates['monotonic'], shift)))[0]
        if correlation_monotonic > first_max_monotonic:
            second_max_monotonic = first_max_monotonic
            first_max_monotonic = correlation_monotonic
            key_index_monotonic = shift

        correlation_difficult = (pearsonr(pcp, np.roll(key_templates['difficult'], shift)))[0]
        if correlation_difficult > first_max_difficult:
            second_max_difficult = first_max_difficult
            first_max_difficult = correlation_difficult
            key_index_difficult = shift



    if (first_max_ionian > first_max_harmonic) and (first_max_ionian > first_max_mixolydian) \
            and (first_max_ionian > first_max_phrygian) and (first_max_ionian > first_max_fifth) \
            and (first_max_ionian > first_max_monotonic) and (first_max_ionian > first_max_difficult):
        key_index = key_index_ionian
        scale = 'ionian'
        first_max = first_max_ionian
        second_max = second_max_ionian

    elif (first_max_harmonic > first_max_ionian) and (first_max_harmonic > first_max_mixolydian) \
            and (first_max_harmonic > first_max_phrygian) and (first_max_harmonic > first_max_fifth) \
            and (first_max_harmonic > first_max_monotonic) and (first_max_harmonic > first_max_difficult):
        key_index = key_index_harmonic
        scale = 'harmonic'
        first_max = first_max_harmonic
        second_max = second_max_harmonic

    elif (first_max_mixolydian > first_max_harmonic) and (first_max_mixolydian > first_max_ionian) \
            and (first_max_mixolydian > first_max_phrygian) and (first_max_mixolydian > first_max_fifth) \
            and (first_max_mixolydian > first_max_monotonic) and (first_max_mixolydian > first_max_difficult):
        key_index = key_index_mixolydian
        scale = 'mixolydian'
        first_max = first_max_mixolydian
        second_max = second_max_mixolydian

    elif (first_max_phrygian > first_max_harmonic) and (first_max_phrygian > first_max_mixolydian) \
            and (first_max_phrygian > first_max_ionian) and (first_max_phrygian > first_max_fifth) \
            and (first_max_phrygian > first_max_monotonic) and (first_max_phrygian > first_max_difficult):
        key_index = key_index_phrygian
        scale = 'phrygian'
        first_max = first_max_phrygian
        second_max = second_max_phrygian

    elif (first_max_fifth > first_max_harmonic) and (first_max_fifth > first_max_mixolydian) \
            and (first_max_fifth > first_max_phrygian) and (first_max_fifth > first_max_ionian) \
            and (first_max_fifth > first_max_monotonic) and (first_max_fifth > first_max_difficult):
        key_index = key_index_fifth
        scale = 'fifth'
        first_max = first_max_fifth
        second_max = second_max_fifth

    elif (first_max_monotonic > first_max_harmonic) and (first_max_monotonic > first_max_mixolydian) \
            and (first_max_monotonic > first_max_phrygian) and (first_max_monotonic > first_max_fifth) \
            and (first_max_monotonic > first_max_ionian) and (first_max_monotonic > first_max_difficult):
        key_index = key_index_monotonic
        scale = 'monotonic'
        first_max = first_max_monotonic
        second_max = second_max_monotonic

    elif (first_max_difficult > first_max_harmonic) and (first_max_difficult > first_max_mixolydian) \
            and (first_max_difficult > first_max_phrygian) and (first_max_difficult > first_max_fifth) \
            and (first_max_difficult > first_max_monotonic) and (first_max_difficult > first_max_ionian):
        key_index = key_index_difficult
        scale = 'difficult'
        first_max = first_max_difficult
        second_max = second_max_difficult

    else:
        key_index = -1
        first_max = -1
        second_max = -1
        scale = 'unknown'

    if key_index < 0:
        raise IndexError("key_index smaller than zero. Could not find key.")
    else:
        first_to_second_ratio = (first_max - second_max) / first_max
        return key_names[int(key_index)], scale, first_max, first_to_second_ratio


def _select_profile_type(profile, templates_dict):
    try:
        return templates_dict[profile]
    except:
        raise KeyError("Unsupported profile: {0}\nvalid profiles are:\n{1}".format(profile, templates_dict.keys()))
