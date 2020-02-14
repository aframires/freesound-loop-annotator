from flask import Flask, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import json
import os
import glob
import errno
import random

app = Flask(__name__, static_url_path='/fslannotator/static', static_folder='/static/')
auth = HTTPBasicAuth()

PATH_TO_FSL10K = "/static/FSL10K"
PATH_TO_ALL_SOUND_IDS = os.path.join(PATH_TO_FSL10K, 'metadata_sound_ids_list.json')
PATH_TO_SOUND_IDS_PER_USER = os.path.join(PATH_TO_FSL10K, 'metadata_sound_ids_list_username.json')
PATH_TO_AC_ANALYSIS = os.path.join(PATH_TO_FSL10K, 'ac_analysis/')
PATH_TO_METADATA = os.path.join(PATH_TO_FSL10K, 'fs_analysis/')
PATH_TO_AUDIO_FILES = os.path.join(PATH_TO_FSL10K,'audio/wav')
PATH_TO_GENRE_FILE = os.path.join(PATH_TO_FSL10K, 'parent_genres.json')
PATH_TO_ANNOTATIONS =  os.path.join(PATH_TO_FSL10K, 'annotations/')
PATH_TO_USERS_FILE = os.path.join(PATH_TO_FSL10K, 'users.json')
METRONOME_SOUND_URL = '/fslannotator' + PATH_TO_FSL10K + '/woodblock.wav'

users =  json.load(open(PATH_TO_USERS_FILE, 'rb')) 
all_sound_ids = json.load(open(PATH_TO_ALL_SOUND_IDS, 'rb')) 
sound_id_user = json.load(open(PATH_TO_SOUND_IDS_PER_USER,'rb'))
genres_file = json.load(open(PATH_TO_GENRE_FILE, 'rb'))

default_N_assign_more_sounds = 5
enable_auto_assign_annotations = False


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return users.get(username) == password
    return False

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def assign_more_sounds_to_user(username, N=default_N_assign_more_sounds):
    # TODO: this function randomly assigns a maximum of N new annotations
    # we should do a real implementation which choses wisely which sounds
    # to assign
    new_ids = random.sample(all_sound_ids, N)
    current_ids = sound_id_user[username]
    new_non_overlapping_ids = list(set(new_ids).difference(current_ids))
    sound_id_user[username] += new_non_overlapping_ids
    json.dump(sound_id_user, open(PATH_TO_SOUND_IDS_PER_USER, 'w'))


@app.route('/fslannotator/assign', methods = ['GET', 'POST'])
@auth.login_required
def assign():
    username = auth.username()
    assign_more_sounds_to_user(username)
    return redirect(url_for('annotator'))


@app.route('/fslannotator/', methods = ['GET', 'POST'])
@auth.login_required
def annotator():
    username = auth.username()
    sound_ids_to_annotate = sound_id_user.get(username, None)    
    if sound_ids_to_annotate is None:
        return 'Sorry, your username does not exist'  
    user_annotations_path = os.path.join(PATH_TO_ANNOTATIONS, username)
    mkdir_p(user_annotations_path)
    n_pages = len(sound_ids_to_annotate)

    if request.method == 'POST':
        # save annotations to json file
        data = request.get_json()
        json.dump(data['answers'], open(os.path.join(user_annotations_path, 'sound-{}.json'.format(data['id'])), 'w'))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    # get latest annoated sound and corresponding page in sound_ids list
    already_annotated_ids = [str(filename.split('-')[1].split('.')[0]) for filename in os.listdir(
        user_annotations_path) if filename.endswith('.json')]

    last_annotated_page = 0
    for sound_id in already_annotated_ids:
        try:
            position = sound_ids_to_annotate.index(sound_id)
            if position + 1 > last_annotated_page:
                last_annotated_page = position + 1
        except ValueError:
            continue

    page = int(request.args.get('p', last_annotated_page + 1))

    if page > len(sound_ids_to_annotate):
        # All sounds have been annotated
        return render_template("finished_annotations.html", N=default_N_assign_more_sounds, enable_auto_assign_annotations=enable_auto_assign_annotations)

    # get a chunk of sounds according to the requested page number
    sound_id = sound_ids_to_annotate[(page-1)]
    metadata = json.load(open(PATH_TO_METADATA + sound_id + '.json', 'rb'))
    loop_name = metadata["name"]
    sound_image = metadata["image"]
    description = metadata["description"]
    
    tags = metadata["tags"]
    tags_to_display = ', '.join(tags)
    
    #instruments = find_instruments_tags(tags)
    guessed_BPM = metadata["annotations"]["bpm"]

    ac_analysis_filename = metadata["preview_url"]
    base_name = ac_analysis_filename[ac_analysis_filename.rfind("/"):ac_analysis_filename.find("-hq")]
    ac_analysis_filename =  base_name + "_analysis.json"
    ac_analysis = json.load(open(PATH_TO_AC_ANALYSIS + ac_analysis_filename, 'rb'))
    if sound_id in genres_file:
        genres = genres_file[sound_id]
    else:
        genres=[]
    tonality = ac_analysis["tonality"]
    space_ind = tonality.find(' ')
    guessed_Key = tonality[0:space_ind]
    guessedMode = tonality[space_ind + 1:]
    audio_file = ()
    audio_file = glob.glob(PATH_TO_AUDIO_FILES + base_name + '*')[0]
    url_to_audio_file = '/fslannotator' + audio_file

    return render_template("index.html", 
                            sound_id=sound_id,
                            page=page,
                            n_pages=n_pages,
                            audio_file=url_to_audio_file,
                            metronome_sound_url=METRONOME_SOUND_URL,
                            loop_name=loop_name,
                            description=description,
                            tags=tags_to_display,
                            sound_image=sound_image,
                            guessedBPM=guessed_BPM,
                            guessedKey=guessed_Key,
                            guessedMode=guessedMode,
                            genres=genres)


if __name__ == '__main__':
    app.run(debug=True)
