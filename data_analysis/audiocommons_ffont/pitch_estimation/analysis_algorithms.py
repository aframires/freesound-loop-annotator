from ac_utils.sound import load_audio_file
import essentia.standard as estd
import subprocess
from numpy import median
from ac_utils.music import frequency_to_midi_note, midi_note_to_note


SOUND_FILE_KEY = 'file_path'


def algorithm_pitch_note_essentia(sound):
    """
    Estimates the note of a given audio file.
    
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """
    results = dict()

    audio = load_audio_file(file_path=sound[SOUND_FILE_KEY], sample_rate=44100)
    frameSize = 1024
    hopsize = frameSize

    # Estimate pitch using PitchYin
    frames = estd.FrameGenerator(audio, frameSize=frameSize, hopSize=hopsize)
    pitchDetect = estd.PitchYin(frameSize=frameSize, sampleRate=44100)
    pitches = []
    confidence = []
    for frame in frames:
        f, conf = pitchDetect(frame)
        pitches += [f]
        confidence += [conf]

    pitches = [pitch for pitch in pitches if pitch > 0]
    if not pitches:
        pitch_median = 0.1
    else:
        pitch_median = median(pitches)
    midi_note = frequency_to_midi_note(pitch_median)
    note = midi_note_to_note(midi_note)
    results.update({'EssentiaPitchYin': {'note': note, 'midi_note': midi_note, 'pitch': pitch_median}})

    # Estimate pitch using PithYinFFT
    frames = estd.FrameGenerator(audio, frameSize=frameSize, hopSize=hopsize)
    pitchDetect = estd.PitchYinFFT(frameSize=frameSize, sampleRate=44100)
    win = estd.Windowing(type='hann')
    pitches = []
    confidence = []
    for frame in frames:
        spec = estd.Spectrum()(win(frame))
        f, conf = pitchDetect(spec)
        pitches += [f]
        confidence += [conf]
    pitches = [pitch for pitch in pitches if pitch > 0]
    if not pitches:
        pitch_median = 0.1
    else:
        pitch_median = median(pitches)
    midi_note = frequency_to_midi_note(pitch_median)
    note = midi_note_to_note(midi_note)
    results.update({'EssentiaPitchYinFFT': {'note': note, 'midi_note': midi_note, 'pitch': pitch_median}})

    return results


def algorithm_pitch_qmul_pyin(sound):
    """
    Estimates the note of a given audio file.
    M. Mauch and S. Dixon, "pYIN: A Fundamental Frequency Estimator Using Probabilistic Threshold Distributions", in 
    Proceedings of the IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 2014), 2014.
    
    See https://code.soundsoftware.ac.uk/projects/pyin
    :param sound: sound dictionary from dataset
    :return: dictionary with results per different methods
    """

    results = dict()
    command_template = 'sonic-annotator -q ' \
                       '-d vamp:pyin:yin:f0 ' \
                       '"{file_path}" ' \
                       '-w csv  --csv-stdout'
    command = command_template.format(
        file_path=sound[SOUND_FILE_KEY]
    )
    print(command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print('\n' + err + '\n')

    pitches = list()
    for line in out.split('\n'):
        try:
            pitches.append(float(line.split(',')[2]))
        except IndexError:
            pass

    pitches = [pitch for pitch in pitches if pitch > 0]
    if not pitches:
        pitch = 0.1
    else:
        pitch = median(pitches)

    midi_note = frequency_to_midi_note(pitch)
    note = midi_note_to_note(midi_note)
    results['QMULpyin'] = {'note': note, 'midi_note': midi_note, 'pitch': pitch}

    return results
