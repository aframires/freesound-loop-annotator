from getsounds import select_relevant_sounds
from flask import Flask, render_template, request, redirect, url_for, session
from flask_httpauth import HTTPBasicAuth
from flask.json import jsonify
from requests_oauthlib import OAuth2Session

import json
import os
import glob
import errno
import random

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__, static_url_path='/fslannotator/static', static_folder='/static')
app.secret_key = os.urandom(24)

PATH_TO_FSL10K = "/static/FSL10K"
PATH_TO_ALL_SOUND_IDS = os.path.join(PATH_TO_FSL10K, 'metadata_sound_ids_list.json')
PATH_TO_USER_FOLDER = os.path.join(PATH_TO_FSL10K, 'annotators/')
PATH_TO_AC_ANALYSIS = os.path.join(PATH_TO_FSL10K, 'ac_analysis/')
PATH_TO_METADATA = os.path.join(PATH_TO_FSL10K, 'fs_analysis/')
PATH_TO_JOINED_METADATA = os.path.join(PATH_TO_FSL10K, "metadata.json")
PATH_TO_AUDIO_FILES = os.path.join(PATH_TO_FSL10K,'audio/wav')
PATH_TO_GENRE_FILE = os.path.join(PATH_TO_FSL10K, 'parent_genres.json')
PATH_TO_ANNOTATIONS =  os.path.join(PATH_TO_FSL10K, 'annotations/')
METRONOME_SOUND_URL = '/fslannotator' + PATH_TO_FSL10K + '/woodblock.wav'

all_sound_ids = json.load(open(PATH_TO_ALL_SOUND_IDS, 'rb')) 
genres_file = json.load(open(PATH_TO_GENRE_FILE, 'rb'))
joined_metadata = json.load(open(PATH_TO_JOINED_METADATA, 'rb'))

default_N_assign_more_sounds = 10
enable_auto_assign_annotations = True

authorization_base_url = 'https://freesound.org/apiv2/oauth2/authorize/'
token_url = 'https://freesound.org/apiv2/oauth2/access_token/'


# The information below is obtained upon registration of new Freesound API
# credentials here: http://freesound.org/apiv2/apply
# See documentation of "Step 3" below to understand how to fill in the 
# "Callback URL" field when registering the new credentials.

client_file = os.path.join(PATH_TO_FSL10K,"client.json")
client_info = json.load(open(client_file, 'rb'))
client_id = client_info["id"]
client_secret = client_info["secret"]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def assign_more_sounds_to_user(username, N=default_N_assign_more_sounds):

    user_sounds_path = os.path.join(PATH_TO_USER_FOLDER, username + '.json')       

    new_ids = select_relevant_sounds(PATH_TO_ANNOTATIONS, joined_metadata, genres_file, all_sound_ids, N)
    current_ids = json.load(open(user_sounds_path, 'rb'))
    new_non_overlapping_ids = list(set(new_ids).difference(current_ids))
    current_ids += new_non_overlapping_ids
    json.dump(current_ids, open(user_sounds_path, 'w'))


@app.route('/fslannotator/assign', methods = ['GET', 'POST'])
def assign():
    assign_more_sounds_to_user(session["username"])
    return redirect(url_for('annotate'))


# Step 2: User authorization, this happens on the provider.

@app.route("/fslannotator/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    Note that the URL at which your app is serving this view is the 
    "Callback URL" that you have to put in the API credentials you create
    at Freesound. If running this code example unchanged, the callback URL 
    should be: http://localhost:5000/callback
    """

    freesound = OAuth2Session(client_id, state=session['oauth_state'])
    token = freesound.fetch_token(token_url, client_secret=client_secret, 
                                  authorization_response=request.url)

    # If you're using the freesound-python client library to access
    # Freesound, this is the token you should use to make OAuth2 requests
    # You should set the token like: 
    #     client.set_token(token,"oauth2")
    
    # However, for this example lets lets save the token and show how to
    # access a protected resource that will return some info about the user account 
    # who has just been authenticated using OAuth2. We redirect to the /profile
    # route of this app which will query Freesound for the user account details.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))

@app.route("/fslannotator/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    freesound = OAuth2Session(client_id, token=session['oauth_token'])
    user_dict = freesound.get('https://freesound.org/apiv2/me').json()

    session["username"] = str(user_dict["unique_id"])

    return redirect(url_for('.annotate'))

    #print(jsonify(freesound.get('https://freesound.org/apiv2/me').json()))
    #return jsonify(freesound.get('https://freesound.org/apiv2/me').json())


@app.route('/fslannotator/login', methods = ['GET', 'POST'])
def login():
    
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Freesound)
    using an URL with a few key OAuth parameters.
    """
    freesound = OAuth2Session(client_id)
    authorization_url, state = freesound.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/fslannotator/')
def welcome():
    return render_template("welcome.html")


@app.route('/fslannotator/annotate/', methods = ['GET', 'POST'])
def annotate():
    

    assigned_sounds_path = os.path.join(PATH_TO_USER_FOLDER, session["username"] + '.json')
    if not os.path.exists(assigned_sounds_path):
        sound_ids_to_annotate = []
        json.dump(sound_ids_to_annotate, open(os.path.join(PATH_TO_USER_FOLDER, session["username"] + '.json'), 'w'))
    else:
        sound_ids_to_annotate = json.load(open(assigned_sounds_path, 'rb'))

    user_annotations_path = os.path.join(PATH_TO_ANNOTATIONS, session["username"])
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
    username = metadata["username"]
    
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
                            username=username,
                            tags=tags_to_display,
                            sound_image=sound_image,
                            guessedBPM=guessed_BPM,
                            guessedKey=guessed_Key,
                            guessedMode=guessedMode,
                            genres=genres)


if __name__ == '__main__':

    app.run(debug=True)
