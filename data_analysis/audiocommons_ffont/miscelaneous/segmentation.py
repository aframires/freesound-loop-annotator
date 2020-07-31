# -*- coding: utf-8 -*-

import numpy as np
from fysom import Fysom
from utils.auto_score.analysis.utils import *
import essentia.standard as estd


class Segmentation(object):

    ### STATE MACHINE

    def on_detecting(self, e):
        self.add_frame = self.detecting_process

    def on_attack(self, e):
        self.add_frame = self.attack_process

    def on_sustain(self, e):
        self.add_frame = self.sustain_process
        self.buffer = []

    def on_onset(self, e):
        self.peak_detect.reset()
        self.ext_fsm.onset()

    def on_peak(self, e):
        self.ext_fsm.peak()

    def on_offset(self, e):
        # Find release point
        sustain = self.buffer[1:]
        release_offset_difference = None
        if len(sustain) > self.max_release_frames:
            release_offset_difference = self.__class__.growing_slope_end(np.flipud(sustain),
                                                                         max_frames=self.max_release_frames,
                                                                         m=self.release_slope_ratio)
        self.ext_fsm.offset(release_offset_difference=release_offset_difference)

    ### END STATE MACHINE

    def __init__(self, params, fsm=None):
        self.onset_threshold = params['onset_threshold']
        self.offset_threshold = params['offset_threshold']
        self.max_attack_time = params['max_attack_time']
        self.max_release_time = params['max_release_time']
        self.attack_slope_ratio = params['attack_slope_ratio']
        self.release_slope_ratio = params['release_slope_ratio']
        self.flux_threshold = params['flux_threshold']
        self.mel_threshold = params['mel_threshold']
        self.rms_threshold = params['rms_threshold']
        self.conf_threshold = params['conf_threshold']
        self.ratio_mel = params['ratio_mel']
        self.ratio_rms = params['ratio_rms']
        self.rms_threshold_value = 0
        self.mel_threshold_vale = 0

        self.fs = params['fs']
        self.hop_size = params['hop_size']
        self.max_attack_frames = seconds2frames(self.max_attack_time, fs=self.fs, hop_size=self.hop_size)
        self.max_release_frames = seconds2frames(self.max_release_time, fs=self.fs, hop_size=self.hop_size)
        self.ext_fsm = fsm  # external state machine to send events to
        self.buffer = []

        self.was_onset = False
        self.was_offset = False
        self.onset_counter = self.offset_counter = None
        self.onset_samples = 2  # number of consecutive samples to be above threshold
        self.offset_samples = 3  # number of consecutive samples to be below threshold
        self.peak_detect = GrowingSlopeEnd(max_frames=self.max_attack_frames, m=self.attack_slope_ratio)

        # essentia algorithms initialization
        self.o_mel = estd.OnsetDetection(method='melflux')
        self.o_rms = estd.OnsetDetection(method='rms')
        self.o_hfc = estd.OnsetDetection(method='hfc')
        self.o_flux = estd.OnsetDetection(method='flux')
        self.o_complex = estd.OnsetDetection(method='complex')
        self.fft = estd.FFT()
        self.c2p = estd.CartesianToPolar()
        self.w = estd.Windowing(type='hann')

        # STATE MACHINE
        self.fsm = Fysom({'initial': 'detecting',
                          'events': [
                              {'name': 'onset', 'src': 'detecting', 'dst': 'attack'},
                              {'name': 'peak', 'src': 'attack', 'dst': 'sustain'},
                              {'name': 'offset', 'src': 'sustain', 'dst': 'detecting'},
                              {'name': 'reset', 'src': ['detecting', 'attack', 'sustain'], 'dst': 'detecting'}
                          ],
                          'callbacks': {
                              'ondetecting': self.on_detecting,
                              'onattack': self.on_attack,
                              'onsustain': self.on_sustain,
                              'onbeforeonset': self.on_onset,
                              'onbeforepeak': self.on_peak,
                              'onbeforeoffset': self.on_offset
                          }})

    def detecting_process(self, loudness, conf, frame):
        mag, phase = self.c2p(self.fft(self.w(frame)))
        mel_onset = self.o_mel(mag, phase)
        rms_onset = self.o_rms(mag, phase)
        flux_onset = self.o_flux(mag, phase)
        if (flux_onset > self.flux_threshold or mel_onset > self.mel_threshold) \
                and rms_onset > self.rms_threshold and loudness > self.onset_threshold:
            if self.was_onset:
                self.onset_counter -= 1
                # store the value of the detection functions to detect sustain relatively to it
                self.rms_threshold_value = rms_onset
                self.mel_threshold_vale = mel_onset
                if self.onset_counter <= 0:
                    self.was_onset = False
                    self.fsm.onset()
            else:
                self.onset_counter = self.onset_samples - 1
            self.was_onset = True
        else:
            self.was_onset = False

    def attack_process(self, loudness, conf, frame):
        mag, phase = self.c2p(self.fft(self.w(frame)))
        rms_onset = self.o_rms(mag, phase)
        mel_onset = self.o_mel(mag, phase)
        if conf > self.conf_threshold and rms_onset < self.rms_threshold_value*self.ratio_rms \
                and mel_onset < self.mel_threshold_vale*self.ratio_mel:
            self.fsm.peak()

    def sustain_process(self, loudness, conf, frame):
        self.buffer.append(loudness)
        if loudness <= self.offset_threshold:
            if self.was_offset:
                self.offset_counter -= 1
                if self.offset_counter <= 0:
                    self.was_offset = False
                    self.fsm.offset()
            else:
                self.offset_counter = self.offset_samples - 1
            self.was_offset = True
        else:
            self.was_offset = False

    # Modification of adaptative efforts to use signal slope
    # Offline version
    @staticmethod
    def growing_slope_end(signal, m=3, threshold_increment=1.5, max_frames=200):
        if signal.any():
            initial_threshold = signal[0]
        else:
            initial_threshold = 0
        current_threshold_time = 0
        current_threshold = initial_threshold
        next_threshold = current_threshold + threshold_increment
        total_slope = -np.inf

        while True:
            try:
                next_threshold_time = np.nonzero(
                    signal[current_threshold_time + 1:] >= next_threshold)[0][0] + current_threshold_time + 1
                next_threshold = signal[next_threshold_time]  # the amplitude point where it has been detected
            except IndexError:
                if current_threshold_time > max_frames:
                    current_threshold_time = max_frames
                break  # if there is no more threshold, the previous one is the final one

            slope = (next_threshold - current_threshold) / float(next_threshold_time - current_threshold_time)

            if slope * m < total_slope:
                if current_threshold_time > max_frames:
                    current_threshold_time = max_frames
                break
            if current_threshold_time > max_frames:
                print 'Warning: could not find a growing slope end'
                current_threshold_time = max_frames
                break

            total_slope = (next_threshold - initial_threshold) / float(next_threshold_time)
            current_threshold_time = next_threshold_time
            current_threshold = next_threshold
            next_threshold += threshold_increment
        return current_threshold_time


class GrowingSlopeEnd(object):
    def __init__(self, m=3, threshold_increment=1.5, max_frames=200):
        self.m = m
        self.threshold_increment = threshold_increment
        self.max_attack_frames = max_frames
        self.total_slope = -np.inf
        self.initial_threshold = None
        self.last_threshold = None
        self.last_threshold_idx = 0
        self.next_threshold = None
        self.frame_idx = -1

    def add_frame(self, loudness):
        """ Returns True if this frame is the peak """
        self.frame_idx += 1

        if self.initial_threshold is None:  # initialize
            self.initial_threshold = self.last_threshold = loudness
            self.last_threshold_idx = self.frame_idx = 0
            self.next_threshold = self.last_threshold + self.threshold_increment
            self.total_slope = -np.inf

        elif self.frame_idx > self.max_attack_frames:
            print 'Warning: could not find a growing slope end'
            return True

        else:
            if loudness >= self.next_threshold:  # a threshold has been surpassed
                self.next_threshold = loudness  # assign the actual value
                slope = (self.next_threshold - self.last_threshold) / float(
                    self.frame_idx - self.last_threshold_idx)  # calculate the slope of the last threshold

                if slope * self.m < self.total_slope:  # peak detected
                    return True

                # Calculate slope from the first frame to this frame
                self.total_slope = (self.next_threshold - self.initial_threshold) / self.frame_idx
                self.last_threshold = self.next_threshold
                self.last_threshold_idx = self.frame_idx
                self.next_threshold += self.threshold_increment

        return False

    def reset(self):
        self.initial_threshold = None
