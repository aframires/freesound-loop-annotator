# Need this to import from parent directory when running outside pycharm
import os
import sys
import shutil
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from scripts.convert_audio_files_to_wav import convert_audio_files_to_wav
from ac_utils.general import save_to_json, create_directories
import click


def parse_audio_file_metatada(metadata_file_path):
    lines = [line.rstrip('\n') for line in open(metadata_file_path)]

    metadata = dict()
    metadata['id'] = metadata_file_path.split('/')[-1].split('.')[0]
    metadata['annotations'] = dict()
    metadata['annotations']['key'] = lines[0]
    return metadata


@click.command()
@click.argument('dataset_path')
def create_giantsteps_dataset(dataset_path):
    """
    Before running this script, get the annotations and data from the dataset repository:
        1) clone https://github.com/GiantSteps/giantsteps-key-dataset
        2) cd to directory and run ./audio_dl.sh
    """

    original_audio_path = os.path.join(dataset_path, 'audio', 'original')
    converted_audio_path = os.path.join(dataset_path, 'audio', 'wav')
    metadata_files_path = os.path.join(dataset_path, 'annotations', 'key')

    if not os.path.exists(original_audio_path):
        click.echo("Moving downloaded audio files to new original path")
        shutil.move(os.path.join(dataset_path, 'audio'), os.path.join(dataset_path, 'original'))
        shutil.move(os.path.join(dataset_path, 'original'), original_audio_path)

    if not os.path.exists(converted_audio_path):
        click.echo("Audio files in the dataset have not been converted to wav, we'll convert them now")
        create_directories([converted_audio_path])
        convert_audio_files_to_wav(original_audio_path, converted_audio_path, 44100, 16, 1, '')
    else:
        click.echo("Converted audio files already exist, no need to convert them")


    metadata = dict()
    with click.progressbar([fname for fname in os.listdir(original_audio_path)],
                           label="Gathering metadata...") as dir_filenames:
        for filename in dir_filenames:
            if filename.endswith('mp3'):
                sound_metadata = parse_audio_file_metatada(
                    os.path.join(metadata_files_path, "%s" % filename).replace('.mp3', '.key'))
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
    create_giantsteps_dataset()
