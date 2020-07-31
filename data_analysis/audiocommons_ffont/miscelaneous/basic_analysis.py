import essentia.standard as estd
import essentia
import matplotlib.pyplot as plt
import seaborn
import numpy as np
import settings
seaborn.set(style="dark")


def seconds2samples(seconds, fs=44100, round=False):
    samples = seconds * fs
    if round:
        samples = np.round(samples)
    return samples


def segment(audio, hopSize, frameSize, rms_onset_threshold, mel_onset_threshold,
            flux_onset_threshold, onset_threshold):

    # init algorithms
    o_mel = estd.OnsetDetection(method='melflux')
    o_rms = estd.OnsetDetection(method='rms')
    o_hfc = estd.OnsetDetection(method='hfc')
    o_flux = estd.OnsetDetection(method='flux')
    fft = estd.FFT()
    c2p = estd.CartesianToPolar()
    pool = essentia.Pool()
    frame_generator = estd.FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize)
    w = estd.Windowing(type='hann')
    yin = estd.PitchYinFFT(frameSize=frameSize, minFrequency=40, maxFrequency=2500, interpolate=True)
    spectrum = estd.Spectrum()
    loudness = estd.Loudness()

    # control parameters
    attack = False
    detection = True
    mel_onset_value = 0
    rms_onset_value = 0

    # output variables
    onset = None
    sustain = None

    for index, frame in enumerate(frame_generator):
        mag, phase = c2p(fft(w(frame)))
        _, conf = yin(spectrum(w(frame)))
        loud = loudness(frame)
        mel_onset = o_mel(mag, phase)
        rms_onset = o_rms(mag, phase)
        hfc_onset = o_hfc(mag, phase)
        flux_onset = o_flux(mag, phase)
        pool.add('onsets_mel', mel_onset)
        pool.add('onsets_rms', rms_onset)
        pool.add('onsets_hfc', hfc_onset)
        pool.add('onsets_flux', flux_onset)
        pool.add('conf', conf)
        pool.add('loudness', loud)

        # condition for onset
        if detection and (flux_onset > flux_onset_threshold or mel_onset > mel_onset_threshold) \
                and rms_onset > rms_onset_threshold and loud > onset_threshold:
            onset = index
            attack = True
            detection = False
            mel_onset_value = mel_onset
            rms_onset_value = rms_onset
        # condition for beginning of sustain
        if attack and conf > 0.5 and rms_onset < rms_onset_value*.05 and mel_onset < mel_onset_value*.3:
            attack = False
            sustain = index
    return onset, sustain


def plot_segmentation(audio, onset, sustain, release=None, offset=None):
        plt.figure()
        plt.vlines(onset, 0, 1, label='attack_init', color='g')
        plt.vlines(sustain, 0, 1, label='sustain_init', color='b')
        plt.vlines(release, 0, 1, label='sustain_end', color='r')
        plt.vlines(offset, 0, 1, label='sustain_end', color='g')
        time = np.linspace(0, len(audio)/512, num=len(audio))
        plt.plot(time, audio)
        plt.show()

# INIT PARAMETERS
# path to the audio file
file_path = settings.DATA_PATH + '/47_58_2.wav'
fs = 44100
hopSize = 512
frameSize = 2048
rms_onset_threshold = 1E-5
mel_onset_threshold = 80
flux_onset_threshold = 0.1
onset_threshold = 0.1
max_attack_time = seconds2samples(0.5, fs)

audio_file = estd.EasyLoader(filename=file_path, sampleRate=fs)
audio = audio_file.compute()

onset, sustain = segment(audio, hopSize, frameSize, rms_onset_threshold, mel_onset_threshold,
                         flux_onset_threshold, onset_threshold)

plot_segmentation(audio, onset, sustain)