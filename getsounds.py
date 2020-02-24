import os
import glob
import json

#I ADDED A DOT HERE !!!!!!!
#PATH_TO_FSL10K = "./static/FSL10K"

#PATH_TO_ALL_SOUND_IDS = os.path.join(PATH_TO_FSL10K, 'metadata_sound_ids_list.json')
#PATH_TO_METADATA = os.path.join(PATH_TO_FSL10K, "metadata.json")
#PATH_TO_GENRES = os.path.join(PATH_TO_FSL10K, "parent_genres.json")
#PATH_TO_ANNOTATIONS =  os.path.join(PATH_TO_FSL10K, 'annotations/')
default_N_assign_more_sounds = 10

#metadata = json.load(open(PATH_TO_METADATA, 'rb'))
#genres_metadata = json.load(open(PATH_TO_GENRES, 'rb'))
#all_sound_ids = json.load(open(PATH_TO_ALL_SOUND_IDS,'rb'))



def compile_annotated_sounds(annotations_path):
    annotated_sounds = {}
    
    annotation_files = glob.glob(annotations_path + '/*/*.json', recursive=True)
    for an_file in annotation_files:
        an = json.load(open(an_file,'rb'))
        #remove the path, then the extension and then the "sound-" string
        sound_id = os.path.basename(os.path.splitext(an_file)[0]).replace('sound-','')
        if sound_id in annotated_sounds:
            annotated_sounds[sound_id] = {  "genres" : list(set(an["genres"] + annotated_sounds[sound_id]["genres"])),
                                            "num_annotations" : annotated_sounds[sound_id]["num_annotations"] + 1   }
        else:
            annotated_sounds[sound_id] = {  "genres" : an["genres"],
                                            "num_annotations" : 1   }

    return annotated_sounds


def collect_authors(sounds_annotated,metadata):
    author_sounds = {}
    for sound in sounds_annotated:
        author = metadata[sound]["username"]
        if author in author_sounds.keys():
            author_sounds[author] = author_sounds[author] + 1
        else:
            author_sounds[author] = 1
        
    return author_sounds


def collect_packs(sounds_annotated,metadata):
    pack_sounds = {}
    for sound in sounds_annotated:
        pack = metadata[sound]["pack_name"]
        if pack is not None:
            if pack in pack_sounds.keys():
                pack_sounds[pack] = pack_sounds[pack] + 1
            else:
                pack_sounds[pack] = 1
        
    return pack_sounds

def collect_genres(sounds_annotated):
    genre_sounds = {}
    for sound in sounds_annotated:
        genres = sounds_annotated[sound]["genres"]
        for genre in genres:
            if genre in genre_sounds.keys():
                genre_sounds[genre] = genre_sounds[genre] + 1
            else:
                genre_sounds[genre] = 1
        
    return genre_sounds
    
def genre_importance(sound_genres, genre_sounds):
    importance = 0
    genre_sounds_sorted = sorted(genre_sounds.items(), key=lambda x: x[1])
    less_annotated_sounds = [genre_sounds_sorted[0][0], genre_sounds_sorted[1][0]]
    for genre in sound_genres:
        if genre in less_annotated_sounds:
            importance = importance + 1
    
    return importance

def discard_packs(all_sound_ids,metadata):
    packs_to_discard = []
    for sound in all_sound_ids:
        if metadata[sound]["pack"] in packs_to_discard:
            all_sounds_ids.remove(sound)

    return all_sound_ids



def select_relevant_sounds(annotations_path, metadata, genre_metadata, all_sound_ids, N=default_N_assign_more_sounds):

    sounds_annotated = compile_annotated_sounds(annotations_path)

    anno_weight=1000
    auth_weight=1
    pack_weight=1
    genre_weight=-10

    authors_sounds = collect_authors(sounds_annotated,metadata)
    pack_sounds = collect_packs(sounds_annotated,metadata)
    genre_sounds = collect_genres(sounds_annotated)
    sounds_to_rate = discard_packs(all_sound_ids,metadata)
    sound_irrelevance_list = []

    for sound in sounds_to_rate:
        num_annotated = 0
        if sounds_annotated.get(sound) != None: 
            num_annotated = sounds_annotated[sound]["num_annotations"]

        num_author = 0
        if authors_sounds.get(metadata[sound]["username"]) != None:
            num_author = authors_sounds[metadata[sound]["username"]]
        
        num_pack = 0
        if pack_sounds.get(metadata[sound]["pack"]) != None:
            num_pack = pack_sounds[metadata[sound]["pack"]]
        
        gen_importance = genre_importance(genre_metadata.get(sound,[]), genre_sounds)
        irrelevance = num_annotated*anno_weight + num_author*auth_weight + num_pack*pack_weight + gen_importance*genre_weight
        sound_irrelevance_list.append((sound,irrelevance))
    
    sound_irrelevance_sorted = sorted(sound_irrelevance_list, key=lambda x: x[1])
    sound_irrelevance_ids = [lis[0] for lis in sound_irrelevance_sorted]
    print(sound_irrelevance_ids[0:N])
    return sound_irrelevance_ids[0:N]

    