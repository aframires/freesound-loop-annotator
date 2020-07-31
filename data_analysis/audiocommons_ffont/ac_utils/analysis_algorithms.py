from ac_utils.sound import load_audio_file
from ac_utils.general import load_from_yaml
import numpy as np
import essentia.standard as estd
import essentia
import os
import settings
import subprocess
import yaml
import json

SOUND_FILE_KEY = 'file_path'


def algorithm_durations(sound):
    """
    Returns the duration of a file according to its length in number of samples and according to an envelope
    computation (See FFont ismir paper TODO: cite correctly).
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """
    results = dict()
    sample_rate = 44100
    n_channels = 1
    audio = load_audio_file(file_path=sound[SOUND_FILE_KEY], sample_rate=sample_rate)
    length_samples = len(audio)
    duration = float(len(audio))/(sample_rate * n_channels)
    # NOTE: load_audio_file will resample to the given sample_rate and downmix to mono

    # Effective duration
    env = estd.Envelope(attackTime=10, releaseTime=10)
    envelope = env(essentia.array(audio))
    threshold = envelope.max() * 0.05
    envelope_above_threshold = np.where(envelope >= threshold)
    start_effective_duration = envelope_above_threshold[0][0]
    end_effective_duration = envelope_above_threshold[0][-1]
    length_samples_effective_duration = end_effective_duration - start_effective_duration

    results['durations'] = {
        'duration': duration,
        'length_samples': length_samples,
        'length_samples_effective_duration': length_samples_effective_duration,
        'start_effective_duration': start_effective_duration,
        'end_effective_duration': end_effective_duration
    }
    return results


def algorithm_freesound_extractor_04(sound):
    out_file_path = os.path.join(settings.TEST_FILES_PATH, str(sound['id']))
    results = dict()
    command = settings.FREESOUND_EXTRACTOR_PATH_04
    p = subprocess.Popen(command.split() + [sound[SOUND_FILE_KEY], out_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print('\n' + err + '\n')
    try:
        analysis_output = load_from_yaml(out_file_path + '_statistics.yaml')
        os.remove(out_file_path + '_frames.json')
        os.remove(out_file_path + '_statistics.yaml')
        results['FS_Extractor_04'] = analysis_output
    except IOError:
        pass
    except yaml.reader.ReaderError:
        pass
    return results


def algorithm_ac_extractor(sound):
    results = dict()
    filename = sound[SOUND_FILE_KEY].split('/')[-1]
    command_template = 'docker run -it --rm ' \
                       '-v {audio_dir}:/essentia ' \
                       '-v {out_dir}:/essentia/out  ' \
                       'audiocommons/ac-audio-extractor ' \
                       '-i "{filename}" -o "out/{filename}.json"'
    command = command_template.format(
        audio_dir='/'.join(sound[SOUND_FILE_KEY].split('/')[:-1]),
        out_dir=settings.TEST_FILES_PATH,
        filename=filename
    )
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print('\n' + err + '\n')
    try:
        out_file_path = os.path.join(settings.TEST_FILES_PATH, filename + '.json')
        analysis_output = json.load(open(out_file_path))
        os.remove(out_file_path)
        results['ACExtractorV1'] = {key.replace('ac:', '').replace('tonality', 'key').replace('tempo', 'bpm'): value for key, value in analysis_output.items()}
    except IOError as e:
        print(e)
    return results


def algorithm_ac_extractor2(sound):
    from algorithms import AudioCommonsV2
    results = dict()
    filepath = sound[SOUND_FILE_KEY]
    analysis_output = AudioCommonsV2.analyze(filepath, compute_timbral_models=False, compute_descriptors_music_pieces=False, compute_descriptors_music_samples=True, out_format="json")
    results['ACExtractorV2'] = {key.replace('temporal_centroid', '##').replace('tonality', 'key').replace('tempo', 'bpm').replace('##', 'temporal_centroid'): value for key, value in analysis_output.items()}  # Rename some concepts
    results['ACExtractorV2r'] = analysis_output  # Store raw output as well
    return results


def algorithm_ac_extractor2_dev(sound):
    from algorithms import AudioCommonsV2dev
    results = dict()
    filepath = sound[SOUND_FILE_KEY]
    analysis_output = AudioCommonsV2dev.analyze(filepath, compute_timbral_models=False, compute_descriptors_music_pieces=False, compute_descriptors_music_samples=True, out_format="json")
    results['ACExtractorV2_dev'] = {key.replace('temporal_centroid', '##').replace('tonality', 'key').replace('tempo', 'bpm').replace('##', 'temporal_centroid'): value for key, value in analysis_output.items()}  # Rename some concepts
    results['ACExtractorV2_dev_r'] = analysis_output  # Store raw output as well
    return results


def algorithm_ac_extractor3_dev(sound):
    from algorithms import AudioCommonsV3dev
    results = dict()
    filepath = sound[SOUND_FILE_KEY]
    analysis_output = AudioCommonsV3dev.analyze(filepath, compute_timbral_models=False, compute_descriptors_music_pieces=False, compute_descriptors_music_samples=True, out_format="json")
    results['ACExtractorV3_dev'] = {key.replace('temporal_centroid', '##').replace('tonality', 'key').replace('tempo', 'bpm').replace('##', 'temporal_centroid'): value for key, value in analysis_output.items()}  # Rename some concepts
    results['ACExtractorV3_dev_r'] = analysis_output  # Store raw output as well
    return results


def algorithm_ac_extractor3(sound):
    from algorithms import AudioCommonsV3
    results = dict()
    filepath = sound[SOUND_FILE_KEY]
    analysis_output = AudioCommonsV3.analyze(filepath, compute_timbral_models=False, compute_descriptors_music_pieces=False, compute_descriptors_music_samples=True, out_format="json")
    results['ACExtractorV3'] = {key.replace('temporal_centroid', '##').replace('tonality', 'key').replace('tempo', 'bpm').replace('##', 'temporal_centroid'): value for key, value in analysis_output.items()}  # Rename some concepts
    return results
