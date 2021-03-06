import os
import glob
import json

default_N_assign_more_sounds = 10
PATH_TO_FSL10K = "/static/FSL10K"
PATH_TO_AC_ANALYSIS = os.path.join(PATH_TO_FSL10K, 'ac_analysis/')
PATH_TO_METADATA = os.path.join(PATH_TO_FSL10K, 'fs_analysis/')


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

def collect_assigned_sounds():
    assigned_sounds = []
    #for key in sound_id_user.keys():
    user_path = os.path.join(PATH_TO_FSL10K, 'annotators/')
    for user_file in os.listdir(user_path):
        if user_file.endswith(".json"):
            assigned_user_sounds = json.load(open(os.path.join(user_path,user_file), 'rb')) 
            for sound in assigned_user_sounds:
                assigned_sounds.append(sound)

    return assigned_sounds


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

    #These weights are used to create an irrelevance metric for each loop
    #based on the existing annotated loops

    #If a loop has been annotated already, multiply the number of times it has been
    #annotated by this weight. 1000 makes sure that we first annotate sounds which
    #haven't been annotated
    anno_weight=500
    #The number of times the author has been annotated should lightly influence the overall
    #irrelevance score. We chose a lower value which allows for more important metrics 
    #such as the number of times annotated to predominate
    auth_weight=1
    #Same applies to the number of times a pack has been annotated
    pack_weight=1
    #The genre importance forces the algorithm to fetch sounds from the less annotated 
    #genres. As gen_importance is proportional to the importance of the loop to be annotated
    #we select a negative weight, to make the loops "less irrelevant"
    genre_weight=-10

    authors_sounds = collect_authors(sounds_annotated,metadata)
    pack_sounds = collect_packs(sounds_annotated,metadata)
    genre_sounds = collect_genres(sounds_annotated)
    sounds_to_rate = discard_packs(all_sound_ids,metadata)
    sound_irrelevance_list = []
    assigned_sounds = collect_assigned_sounds()

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

        num_assigned = assigned_sounds.count(sound)
        
        gen_importance = genre_importance(genre_metadata.get(sound,[]), genre_sounds)
        irrelevance = (num_annotated+num_assigned)*anno_weight + num_author*auth_weight + num_pack*pack_weight + gen_importance*genre_weight

        ac_analysis_filename = metadata[sound]["preview_url"]
        base_name = ac_analysis_filename[ac_analysis_filename.rfind("/"):ac_analysis_filename.find("-hq")]
        ac_analysis_filename =  base_name + "_analysis.json"


        if os.path.exists(PATH_TO_AC_ANALYSIS + ac_analysis_filename):
            sound_irrelevance_list.append((sound,irrelevance))
    
    sound_irrelevance_sorted = sorted(sound_irrelevance_list, key=lambda x: x[1])
    sound_irrelevance_ids = [lis[0] for lis in sound_irrelevance_sorted]
    return sound_irrelevance_ids[0:N]

    