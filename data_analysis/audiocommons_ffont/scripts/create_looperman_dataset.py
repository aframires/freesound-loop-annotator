# Need this to import from parent directory when running outside pycharm
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from scripts.convert_audio_files_to_wav import convert_audio_files_to_wav
from ac_utils.general import save_to_json, create_directories
import click
import hashlib


def parse_audio_file_metatada(metadata_file_path):
    metadata = dict()
    lines = [line.rstrip('\n') for line in open(metadata_file_path)]
    for line in lines:
        if 'artist:' in line:
            metadata['artist'] = line.split('artist: ')[1]
        if 'category:' in line:
            metadata['category'] = line.split('category: ')[1]
        if 'title:' in line:
            metadata['name'] = line.split('title: ')[1]
        if 'description:' in line:
            metadata['description'] = line.split('description: ')[1]
        if 'genre:' in line:
            metadata['genre'] = line.split('genre: ')[1]
        if 'download_url:' in line:
            metadata['id'] = hashlib.md5(b'%s' % line.split('download_url: ')[1]).hexdigest()
        if 'tempo:' in line:
            bpm = float(line.split('tempo: ')[1].split(' bpm')[0])
            # Check that bpm is integer, otherwise return false and do not include it in dataset
            if bpm - int(bpm) != 0.0:
                return False
            if bpm == 0:
                return False
            metadata['annotations'] = {'bpm': int(bpm)}
    return metadata


@click.command()
@click.argument('dataset_path')
def create_looperman_dataset(dataset_path):
    """
    Analyze audio and metadata folder from looperman dataset path and create matadata.json file with all gathered
    information. If downsampled wav files are not present, this command will also create them.
    The dataset_path that is given needs to already contain a directory structure with original files and metadata
    files from looperman.
    """
    metadata_files_path = os.path.join(dataset_path, 'metadata')
    original_audio_path = os.path.join(dataset_path, 'audio', 'original')
    converted_audio_path = os.path.join(dataset_path, 'audio', 'wav')

    if not os.path.exists(converted_audio_path):
        click.echo("Audio files in the dataset have not been converted to wav, we'll convert them now")
        create_directories([dataset_path, converted_audio_path])
        convert_audio_files_to_wav(original_audio_path, converted_audio_path, 44100, 16, 1, '')
    else:
        click.echo("Converted audio files already exist, no need to convert them")

    metadata = dict()
    with click.progressbar([fname for fname in os.listdir(original_audio_path)],
                           label="Gathering metadata...") as dir_filenames:
        for filename in dir_filenames:
            sound_metadata = parse_audio_file_metatada(os.path.join(metadata_files_path, "%s.txt" % filename))
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
    create_looperman_dataset()
