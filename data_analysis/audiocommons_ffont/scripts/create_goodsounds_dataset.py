# Need this to import from parent directory when running outside pycharm
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from pitch_estimation.analysis_algorithms import midi_note_to_note
from ac_utils.general import save_to_json, create_directories
import click
import shutil
import csv
import hashlib


def parse_audio_file_metatada(row):
    metadata = dict()
    metadata['id'] = hashlib.md5(b'%s-%s' % (row[14], row[13])).hexdigest()
    metadata['annotations'] = dict()
    metadata['annotations']['midi_note'] = int(row[23]) + 12
    metadata['annotations']['note'] = '%s%i' % (row[2], int(row[3]))
    return metadata


def get_pack_by_id(pid, packs_metadata):
    for pack in packs_metadata:
        if pack[0] and pid:
            if int(pack[0]) == int(pid):
                return pack
    return None


@click.command()
@click.argument('dataset_path')
def create_dataset(dataset_path):
    """

    """

    converted_audio_path = os.path.join(dataset_path, 'audio', 'wav')
    sounds_metadata = csv.reader(open(os.path.join(dataset_path, 'goodsounds_sounds_metadata.csv')))
    packs_metadata = [item for item in csv.reader(open(os.path.join(dataset_path, 'goodsounds_packs_metadata.csv')))]
    create_directories([converted_audio_path])
    metadata = dict()
    with click.progressbar([row for row in sounds_metadata],
                           label="Gathering metadata...") as csv_rows:
        for csv_row in csv_rows:
            filename = csv_row[13]
            pack_row = get_pack_by_id(csv_row[14], packs_metadata)
            if pack_row is None:
                continue
            pack_name = pack_row[1]
            file_path = os.path.join(dataset_path, 'sound_files', pack_name, 'neumann', filename)
            new_filename = '%s-%s' % (pack_name, filename)
            dest_path = os.path.join(converted_audio_path, new_filename)

            if not os.path.exists(dest_path):
                try:
                    shutil.move(file_path, dest_path)
                except IOError:
                    continue

            sound_metadata = parse_audio_file_metatada(csv_row)
            if sound_metadata:
                wav_sound_path = "audio/wav/%s" % new_filename
                sound_metadata['wav_sound_path'] = wav_sound_path
                if os.path.exists(os.path.join(dataset_path, sound_metadata['wav_sound_path'])):
                    metadata[sound_metadata['id']] = sound_metadata

    save_to_json(os.path.join(dataset_path, 'metadata.json'), metadata)
    click.echo('Created dataset with %i sounds' % len(metadata))
    click.echo('Saved in %s' % dataset_path)


if __name__ == '__main__':
    create_dataset()
