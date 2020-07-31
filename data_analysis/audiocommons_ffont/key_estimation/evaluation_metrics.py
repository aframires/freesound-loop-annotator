from ..ac_utils.general import vfkp
from ..ac_utils.music import root_to_num
import mir_eval


def is_same_key(key_scale_tuple_a, key_scale_tuple_b, accept_relative_minor=False):
    key_a, scale_a = key_scale_tuple_a
    key_b, scale_b = key_scale_tuple_b

    try:
        scale_a = scale_a.lower()
        scale_b = scale_b.lower()
    except AttributeError:
        pass

    try:
        key_a_num = root_to_num(key_a)
        key_b_num = root_to_num(key_b)
    except KeyError:
        return False

    # Try exact match first
    if key_a_num == key_b_num and scale_a == scale_b:
        return True

    if accept_relative_minor:
        # If indicated, try relative minor too

        # Case key_a is relative minor of key_b
        if key_a_num - key_b_num == 3 and (scale_a == 'major' and scale_b == 'minor'):
            return True

        # Case key_b is relative minor of key_a
        if key_b_num - key_a_num == 3 and (scale_b == 'major' and scale_a == 'minor'):
            return True

    return False


def exact_match(data, method, sound_ids=None):
    """
    Compares estimated tonality with annotated tonality of provided data. 
    Considers as good estimates only exact matches.
    :param data: sound data with annotations and analysis
    :param method: analysis algorithm name to compare with annotation
    :param sound_ids: ids of the sounds to include in comparison (default=None, all found in data)
    :return: list with 1 for sounds that match and 0 for sounds that do not match
    """
    if sound_ids is None:
        sound_ids = data.keys()
    output = list()
    for sound_id in sound_ids:
        ground_truth_value = data[sound_id]['annotations']['key']
        gt_key, gt_scale = ground_truth_value.split(' ')
        try:
            estimated_value = vfkp(data[sound_id]['analysis'], method + '.key', ignore_non_existing=False)
            e_key, e_scale = estimated_value.split(' ')
        except (KeyError, AttributeError):
            e_key = e_scale = None

        if is_same_key((e_key, e_scale), (gt_key, gt_scale)):
            output.append(1)
        else:
            output.append(0)

    return output


def mireval_same(reference_key, estimated_key):
    """
    This code is adapted form mireval.key.weighted_score to consider only relative (3rd) relations
    """
    from mir_eval.key import validate, split_key_string

    validate(reference_key, estimated_key)
    reference_key, reference_mode = split_key_string(reference_key)
    estimated_key, estimated_mode = split_key_string(estimated_key)

    # If keys are the same, return 1.
    if reference_key == estimated_key and reference_mode == estimated_mode:
        return 1.0

    if reference_key == estimated_key and reference_mode == "none":
        return 1.0   
    if reference_key == estimated_key and reference_mode == "unknown":
        return 1.0   
    return 0.0


def mireval_fifth(reference_key, estimated_key):
    """
    This code is adapted form mireval.key.weighted_score to consider only perfect fifth relations
    """
    from mir_eval.key import validate, split_key_string

    validate(reference_key, estimated_key)
    reference_key, reference_mode = split_key_string(reference_key)
    estimated_key, estimated_mode = split_key_string(estimated_key)

    # If keys are the same mode and a perfect fifth (differ by 7 semitones)
    if (estimated_mode == reference_mode and
            (estimated_key - reference_key) % 12 == 7):
        return 1.0
    if (reference_mode == 'none' and 
            (estimated_key - reference_key) % 12 == 7):
        return 1.0
    if (reference_mode == 'unknown' and 
            (estimated_key - reference_key) % 12 == 7):
        return 1.0
    return 0.0


def mireval_relative(reference_key, estimated_key):
    """
    This code is adapted form mireval.key.weighted_score to consider only relative (3rd) relations
    """
    from mir_eval.key import validate, split_key_string

    validate(reference_key, estimated_key)
    reference_key, reference_mode = split_key_string(reference_key)
    estimated_key, estimated_mode = split_key_string(estimated_key)

    # Estimated key is relative minor of reference key (9 semitones)
    if (estimated_mode != reference_mode == 'major' and
            (estimated_key - reference_key) % 12 == 9):
        return 1.0
    # Estimated key is relative major of reference key (3 semitones)
    if (estimated_mode != reference_mode == 'minor' and
            (estimated_key - reference_key) % 12 == 3):
        return 1.0
    return 0.0


def mireval_parallel(reference_key, estimated_key):
    """
    This code is adapted form mireval.key.weighted_score to consider only parallel relations
    """
    from mir_eval.key import validate, split_key_string

    validate(reference_key, estimated_key)
    reference_key, reference_mode = split_key_string(reference_key)
    estimated_key, estimated_mode = split_key_string(estimated_key)

    # If keys are in different modes and parallel (same key name)
    if reference_mode not in ['none','unknown']:
        if estimated_mode != reference_mode and reference_key == estimated_key:
            return 1.0
    return 0.0


def _mireval_key_base_scroe(eval_metric, data, method, sound_ids=None):
    if sound_ids is None:
        sound_ids = data.keys()
    output = list()
    for sound_id in sound_ids:
        ground_truth_value = data[sound_id]['annotations']['key'] 
        try:
            estimated_value = vfkp(data[sound_id]['analysis'], method + '.key', ignore_non_existing=False)
        except (KeyError, AttributeError):
            estimated_value = None

        if estimated_value is not None:
            output.append(eval_metric(ground_truth_value, estimated_value))
        else:
            output.append(0)

    return output


def mireval_key_weighted_score(data, method, sound_ids=None):
    """
    Returns the weighted score for key comparison as implemented in mir_eval library.
    https://craffel.github.io/mir_eval/#module-mir_eval.key.
    
    Relationship	                                        Score
    -------------------------------------------------------------
    Same key	                                            1.0
    Estimated key is a perfect fifth above reference key	0.5
    Relative major/minor	                                0.3
    Parallel major/minor	                                0.2
    Other	                                                0.0
    
    :param data: sound data with annotations and analysis
    :param method: analysis algorithm name to compare with annotation
    :param sound_ids: ids of the sounds to include in comparison (default=None, all found in data)
    :return: list with weighted score for each individual comparison
    """
    return _mireval_key_base_scroe(mir_eval.key.weighted_score, data, method, sound_ids)


def mireval_key_fifth(data, method, sound_ids=None):
    return _mireval_key_base_scroe(mireval_fifth, data, method, sound_ids)


def mireval_key_relative(data, method, sound_ids=None):
    return _mireval_key_base_scroe(mireval_relative, data, method, sound_ids)


def mireval_key_parallel(data, method, sound_ids=None):
    return _mireval_key_base_scroe(mireval_parallel, data, method, sound_ids)


def mireval_key_same(data, method, sound_ids=None):
    return _mireval_key_base_scroe(mireval_same, data, method, sound_ids)

