import csv
import json

annotations_dict = {}
with open('./loop_annotation_data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sound_id = row.pop("sound_id", None)
        if sound_id not in annotations_dict.keys():
            annotations_dict[sound_id] = [row]
        else:
            annotations_dict[sound_id].append(row)


json.dump(annotations_dict, open("annotation_dict.json", 'w'))

keys = ['instrumentation_percussion', 'instrumentation_bass', 'instrumentation_melody', 'instrumentation_chords',
        'instrumentation_fx', 'instrumentation_vocal', 'bpm', 'signature', 'well_cut', 'key', 'mode',
        'genre_bass_music', 'genre_live_sounds', 'genre_cinematic', 'genre_global', 'genre_hip_hop','genre_house_techno','genre_other_dance_music']

#a = 1 and 2 say yes
#b = 1 says yes, 2 says no
#c = 1 says no, 2 says yes
#d = 1 and 2 say no
#e = one of the annotators does not know and the other knows

raw_agreement = {}
for key in keys:
    if key in ['bpm', 'signature', 'key', 'mode']:
        raw_agreement[key] = {'a':0,'b':0,'e':0}
    else:
        raw_agreement[key] = {'a':0,'b':0,'c':0,'d':0}

for sid in annotations_dict:
    if len(annotations_dict[sid]) == 2:
        if (annotations_dict[sid][0]['discard'] == 'False') and (annotations_dict[sid][1]['discard'] == 'False'):
            for key in keys:
                if key in ['bpm', 'signature', 'key', 'mode']:
                    if annotations_dict[sid][0][key] == annotations_dict[sid][1][key]:
                        raw_agreement[key]['a'] += 1
                    elif (annotations_dict[sid][0][key] == 'unknown') or (annotations_dict[sid][1][key] == 'unknown')\
                        or (annotations_dict[sid][0][key] == 'None') or (annotations_dict[sid][1][key] == 'None'):
                        raw_agreement[key]['e'] += 1
                    else:
                        raw_agreement[key]['b'] += 1
                else:

                    if (annotations_dict[sid][0][key] == 'True') and (annotations_dict[sid][1][key] == 'True'):
                        raw_agreement[key]['a'] += 1
                    elif (annotations_dict[sid][0][key] == 'True') and (annotations_dict[sid][1][key] == 'False'):
                        raw_agreement[key]['b'] += 1
                    elif (annotations_dict[sid][0][key] == 'False') and (annotations_dict[sid][1][key] == 'True'):
                        raw_agreement[key]['c'] += 1
                    elif (annotations_dict[sid][0][key]) == 'False' and (annotations_dict[sid][1][key] == 'False'):
                        raw_agreement[key]['d'] += 1

for key in keys:
    print(raw_agreement[key])
    if key in ['bpm', 'signature', 'key', 'mode']:
        print(key + ": agreement - " + "{:.2f}".format(100*(raw_agreement[key]['a']/(raw_agreement[key]['a'] + raw_agreement[key]['b'] + raw_agreement[key]['e']))) + "\%")
        print(key + ": agreement w/ unknown - " + "{:.2f}".format(100*(raw_agreement[key]['a'] + raw_agreement[key]['e'])/(raw_agreement[key]['a'] + raw_agreement[key]['b'] + raw_agreement[key]['e']))+ "\%")

    else:
        print(key + ": agreement - " + "{:.2f}".format(100*(raw_agreement[key]['a'] + raw_agreement[key]['d'])/(raw_agreement[key]['a'] + raw_agreement[key]['b'] + raw_agreement[key]['c'] + raw_agreement[key]['d']))+ "\%")
        print(key + ": positive agreement - " + "{:.2f}".format(100*(2 * raw_agreement[key]['a'])/(2 * raw_agreement[key]['a'] + raw_agreement[key]['b'] + raw_agreement[key]['c']))+ "\%")
        print(key + ": negative agreement - " + "{:.2f}".format(100*(2 * raw_agreement[key]['d'])/(2 * raw_agreement[key]['d'] + raw_agreement[key]['b'] + raw_agreement[key]['c']))+ "\%")

json.dump(raw_agreement, open("raw_agreement_2020_06_16.json", 'w'))




