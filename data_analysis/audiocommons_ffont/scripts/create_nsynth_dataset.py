# Need this to import from parent directory when running outside pycharm
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from pitch_estimation.analysis_algorithms import midi_note_to_note
from ac_utils.general import save_to_json
import click
import json


def parse_audio_file_metatada(nsynth_metadata):
    metadata = dict()
    metadata['id'] = nsynth_metadata['note']
    metadata['annotations'] = dict()
    metadata['annotations']['midi_note'] = nsynth_metadata['pitch']
    metadata['annotations']['note'] = midi_note_to_note(nsynth_metadata['pitch'])
    return metadata


@click.command()
@click.argument('dataset_path')
def create_dataset(dataset_path):
    """
    1) Download nsynth (e.g. test) from https://magenta.tensorflow.org/datasets/
    2) create a folder named 'wav' inside 'audio' folder and move all files to 'wav'
    3) run this script
    """

    converted_audio_path = os.path.join(dataset_path, 'audio', 'wav')
    original_audio_path = converted_audio_path
    nsynth_metadata = json.load(open(os.path.join(dataset_path, 'examples.json')))

    metadata = dict()
    with click.progressbar([fname for fname in os.listdir(original_audio_path)],
                           label="Gathering metadata...") as dir_filenames:
        for filename in dir_filenames:
            if filename.endswith('wav'):
                try:
                    nsynth_sound_metadata = nsynth_metadata[filename.replace('.wav', '')]
                except KeyError:
                    continue

                sound_metadata = parse_audio_file_metatada(nsynth_sound_metadata)
                if sound_metadata:
                    sound_metadata['original_sound_path'] = 'audio/original/%s' % filename
                    filename, extension = os.path.splitext(filename)
                    wav_sound_path = "audio/wav/%s.wav" % filename
                    sound_metadata['wav_sound_path'] = wav_sound_path
                    if os.path.exists(os.path.join(dataset_path, sound_metadata['wav_sound_path'])):
                        metadata[sound_metadata['id']] = sound_metadata

    save_to_json(os.path.join(dataset_path, 'metadata.json'), metadata)
    click.echo('Created dataset with %i sounds' % len(metadata))
    click.echo('Saved in %s' % dataset_path)


if __name__ == '__main__':
    create_dataset()
