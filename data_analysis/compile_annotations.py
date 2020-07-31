import fnmatch
import json
import csv
import os
 
 
def get_filenames_in_dir(dir_name, keyword='*', skip_foldername='', match_case=True, verbose=True):
    names = []
    folders = []
    fullnames = []

    if verbose:
        print(dir_name)

    # check if the folder exists
    if not os.path.isdir(dir_name):
        if verbose:
            print("Directory doesn't exist!")
        return [], [], []

    # if the dir_name finishes with the file separator,
    # remove it so os.walk works properly
    dir_name = dir_name[:-1] if dir_name[-1] == os.sep else dir_name

    # walk all the subdirectories
    for (path, dirs, files) in os.walk(dir_name):
        for f in files:
            hasKey = (fnmatch.fnmatch(f, keyword) if match_case else
                      fnmatch.fnmatch(f.lower(), keyword.lower()))
            if hasKey and skip_foldername not in path.split(os.sep)[1:]:
                try:
                    folders.append(str(path, 'utf-8'))
                except TypeError:  # already unicode
                    folders.append(path)
                try:
                    names.append(str(f, 'utf-8'))
                except TypeError:  # already unicode
                    names.append(path)
                fullnames.append(os.path.join(path, f))
    if verbose:
        print("> Found " + str(len(names)) + " files.")
    return fullnames, folders, names
 
# first copy annotations folder from server:
# scp -r asplab@asplab-web4.s.upf.edu:/mnt/asplab-web/asplab-shared/fsloops-annotator/FSL10K/annotations ~/Dropbox/Loops \script/
 
csv_rows = []
csv_column_keys_labels = [
    ('sound_id', 'sound_id'),
    ('annotator', 'annotator'),
    ('discard', 'discard'),
    ('instrumentation.percussion', 'instrumentation_percussion'),
    ('instrumentation.bass', 'instrumentation_bass'),
    ('instrumentation.chords', 'instrumentation_chords'),
    ('instrumentation.melody', 'instrumentation_melody'),
    ('instrumentation.fx', 'instrumentation_fx'),
    ('instrumentation.vocal', 'instrumentation_vocal'),
    ('bpm', 'bpm'),
    ('well_cut', 'well_cut'),  # No steady bpm data?
    ('signature', 'signature'),
    ('key', 'key'),
    ('mode', 'mode'),
    ('genres.bass music', 'genre_bass_music'),
    ('genres.live sounds', 'genre_live_sounds'),
    ('genres.cinematic', 'genre_cinematic'),
    ('genres.global', 'genre_global'),
    ('genres.hip hop', 'genre_hip_hop'),
    ('genres.house / techno', 'genre_house_techno'),
    ('genres.other dance music', 'genre_other_dance_music'),
    ('comments', 'comments')
]
 
with open('loop_annotation_data.csv', 'w') as csvfile:
    fieldnames = [label for _, label in csv_column_keys_labels]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
 
    csv_rows = []
 
    for filename in get_filenames_in_dir('annotations/', 'sound-*.json')[0]:
        annotator = filename.split('/')[1]
        sound_id = int(filename.split('sound-')[1].split('.json')[0]) 
        annotations = json.load(open(filename))
        annotations.update({
            'annotator': annotator,
            'sound_id': sound_id
        })
  
        flattened_annotations = {}
        for key, label in csv_column_keys_labels:
            try:
                value = annotations[key]
            except KeyError:
                if key.startswith('instrumentation'):
                    value = annotations['instrumentation'][key.split('.')[1]]
                elif key.startswith('genres'):
                    value = key.split('.')[1] in annotations['genres']
            if key == 'comments':
                value = value.encode('utf-8')     
            flattened_annotations[label] = value
 
        csv_rows.append(flattened_annotations)
 
    csv_rows = sorted(csv_rows,  key=lambda x: x['sound_id'])
    writer.writerows(csv_rows)
 
print('Done!')