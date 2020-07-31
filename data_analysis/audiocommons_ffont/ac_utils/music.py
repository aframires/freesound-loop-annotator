import math

NOTE_ROOTS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_ROOTS_EQUIVALENCES = {
    '': '',
}


def root_to_num(root):
    return {
        'A': 0,
        'A#': 1,
        'Bb': 1,
        'B': 2,
        'Cb': 2,
        'B#': 3,
        'C': 3,
        'C#': 4,
        'Db': 4,
        'D': 5,
        'D#': 6,
        'Eb': 6,
        'E': 7,
        'E#': 8,
        'F': 8,
        'F#': 9,
        'Gb': 9,
        'G': 10,
        'G#': 11,
        'Ab': 11,
        None: -1,
    }[root]


def num_to_root(num):
    return {
        0: 'A',
        1: 'A#',
        2: 'B',
        3: 'C',
        4: 'C#',
        5: 'D',
        6: 'D#',
        7: 'E',
        8: 'F',
        9:'F#',
        10: 'G',
        11: 'G#',
        -1: None,
    }[num]


def clean_note_name(note):
    # Make sure that note root is in NOTE_ROOTS, ignore octave info if provided
    if len(note) == 2:
        root = note[0]
        octave = int(note[1])
    elif len(note) > 2:
        root = note[0:2]
        octave = int(note[2:])
    else:
        root = None
        octave = -1

    if root in NOTE_ROOTS:
        return note
    else:
        root = num_to_root(root_to_num(root))
        return '%s%i' % (root, octave)


def midi_note_to_note(midi_note):
    # Use convention MIDI value 69 = 440.0 Hz = A4
    note = midi_note % 12
    octave = midi_note // 12
    return '%s%i' % (NOTE_ROOTS[note], octave - 1)


def frequency_to_midi_note(frequency):
    # Use convention MIDI value 69 = 440.0 Hz = A4
    return int(round(69 + (12 * math.log(frequency / 440.0)) / math.log(2)))


def note_to_midi_note(note):
    # Use convention MIDI value 69 = 440.0 Hz = A4
    if '-' not in note:
        root, octave = (note[0:-1], int(note[-1]))
    else:
        # Case octave number is negative and takes 2 chars
        root, octave = (note[0:-2], int(note[-2:]))
    if root not in NOTE_ROOTS:
        raise Exception('Invalid root %s' % root)
    midi_note = (octave + 1) * 12 + NOTE_ROOTS.index(root)
    return midi_note
