from ac_utils.general import vfkp


def exact_match(data, method, sound_ids=None):
    """
    Compares the estimated note with the reference note expecting an exact match
    :param data: sound data with annotations and analysis
    :param method: analysis algorithm name to compare with annotation
    :param sound_ids: ids of the sounds to include in comparison (default=None, all found in data)
    :return: list with 1 for sounds that match and 0 for sounds that do not match
    """
    if sound_ids is None:
        sound_ids = data.keys()
    output = list()
    for sound_id in sound_ids:
        ground_truth_value = data[sound_id]['annotations']['midi_note']
        try:
            estimated_value = vfkp(data[sound_id]['analysis'], method + '.midi_note', ignore_non_existing=False)
        except KeyError:
            try:
                estimated_value = vfkp(data[sound_id]['analysis'], method + '.note_midi', ignore_non_existing=False)
            except KeyError:
                estimated_value = None

        if estimated_value is not None:
            if int(estimated_value) == int(ground_truth_value):
                output.append(1)
            else:
                output.append(0)
        else:
            output.append(0)

    return output


def pitch_class(data, method, sound_ids=None):
    """
    Compares the estimated note with the reference note expecting an exact match or an octave error (pitch class)
    :param data: sound data with annotations and analysis
    :param method: analysis algorithm name to compare with annotation
    :param sound_ids: ids of the sounds to include in comparison (default=None, all found in data)
    :return: list with 1 for sounds that match and 0 for sounds that do not match
    """
    if sound_ids is None:
        sound_ids = data.keys()
    output = list()
    for sound_id in sound_ids:
        ground_truth_value = data[sound_id]['annotations']['midi_note']
        try:
            estimated_value = vfkp(data[sound_id]['analysis'], method + '.midi_note', ignore_non_existing=False)
        except KeyError:
            try:
                estimated_value = vfkp(data[sound_id]['analysis'], method + '.note_midi', ignore_non_existing=False)
            except KeyError:
                estimated_value = None

        if estimated_value is not None:
            if (int(estimated_value) - int(ground_truth_value)) % 12 == 0:
                output.append(1)
            else:
                output.append(0)
        else:
            output.append(0)

    return output
