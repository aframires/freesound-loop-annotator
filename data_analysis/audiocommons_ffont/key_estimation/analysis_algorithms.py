from ac_utils.sound import load_audio_file
import essentia.standard as estd
from collections import Counter
import subprocess


SOUND_FILE_KEY = 'file_path'


def algorithm_tonal_key_essentia_basic(sound):
    """
    Estimates the tonality of a given audio file.
    See http://essentia.upf.edu/documentation/reference/std_KeyExtractor.html.
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """
    results = dict()

    audio = load_audio_file(file_path=sound[SOUND_FILE_KEY], sample_rate=44100)

    key_extractor = estd.KeyExtractor()
    key, scale, strength = key_extractor(audio)
    results['EssentiaBasic'] = {'key': '%s %s' % (key, scale), 'strength': strength}

    return results


def algorithm_tonal_edmkey(sound):
    """
    Estimate key of a given audio file as described in:
    Faraldo, A., Jorda S., & Herrera P. (In Press).  A Multi-Profile Method for Key Estimation in EDM. AES 
    International Conference on Semantic Audio. See http://mtg.upf.edu/node/3767 
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """
    from algorithms.Edmkey.edmkey_essentia import estimate_key

    results = dict()
    try:
        key, confidence = estimate_key(sound[SOUND_FILE_KEY])
        results['Edmkey'] = {'key': key.replace('\t', ' '), 'confidence': float(confidence)}

        key, confidence = estimate_key(sound[SOUND_FILE_KEY], key_profile='krumhansl')
        results['EdmkeyKrumhansl'] = {'key': key.replace('\t', ' '), 'confidence': float(confidence)}

        key, confidence = estimate_key(sound[SOUND_FILE_KEY], key_profile='temperley05')
        results['EdmkeyTemperley'] = {'key': key.replace('\t', ' '), 'confidence': float(confidence)}

        key, confidence = estimate_key(sound[SOUND_FILE_KEY], key_profile='shaath')
        results['EdmkeyShaath'] = {'key': key.replace('\t', ' '), 'confidence': float(confidence)}

    except IndexError:
        pass

    return results


def algorithm_tonal_qmul_key_detector(sound):
    """
    Estimate key of a given audio file using QMUL's key detector.
    K. Noland and M. Sandler. Signal Processing Parameters for Tonality Estimation. In Proceedings of Audio Engineering 
    Society 122nd Convention, Vienna, 2007.
    See http://vamp-plugins.org/plugin-doc/qm-vamp-plugins.html#qm-keydetector
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """

    results = dict()
    command_template = 'sonic-annotator ' \
                       '-d vamp:qm-vamp-plugins:qm-keydetector:key ' \
                       '"{file_path}" ' \
                       '-w csv  --csv-stdout'
    command = command_template.format(
        file_path=str(sound[SOUND_FILE_KEY])
    )
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print('\n' + str(err) + '\n')

    keys = list()
    for line in out.decode().split('\n'):
        try:
            keys.append(line.split(',')[3])
        except IndexError:
            pass

    if not keys:
        key = None
    else:
        key = Counter(keys).most_common(1)[0][0].replace('\"', '')  # Take the most common key
        if '(unknown)' in key:
            key = None
        elif '/' in key:
            key = key.split('/ ')[1]
    results['QMULKeyDetector'] = {'key': key}

    return results
