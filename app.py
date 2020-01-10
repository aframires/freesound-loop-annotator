#Imagem esta muito grande


from flask import Flask, render_template, request
import json
import os
import glob


app = Flask(__name__, static_url_path='/static')

PATH_TO_FSL10K = "/mnt/f/Code/research/FSL10K"
PATH_TO_SOUND_IDS = os.path.join(PATH_TO_FSL10K, 'metadata_sound_ids_list.json')
PATH_TO_AC_ANALYSIS = os.path.join(PATH_TO_FSL10K, 'ac_analysis/')
PATH_TO_METADATA = os.path.join(PATH_TO_FSL10K, 'fs_analysis/')
PATH_TO_AUDIO_FILES = os.path.join(PATH_TO_FSL10K,'audio/original')

def find_genre_tags(tags):
    return

def find_instruments_tags(tags):
    return


@app.route('/', methods = ['GET', 'POST'])
def annotator():
    if request.method == 'POST':
        # save annotations to json file
        data = request.get_json()
        json.dump(data['answers'], open('annotations/sound-{}.json'.format(data['id']), 'w'))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    page = int(request.args.get('p', 1))
    sound_ids = json.load(open(PATH_TO_SOUND_IDS, 'rb'))

    # get a chunk of sounds according to the requested page number
    sound_id = sound_ids[(page-1)]
    print(sound_id)
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
    tonality = ac_analysis["tonality"]
    space_ind = tonality.find(' ')
    guessed_Key = tonality[0:space_ind]
    guessedMode = tonality[space_ind + 1:]
    #genres = find_genre_tags(tags)
    audio_file = ()
    audio_file = glob.glob(PATH_TO_AUDIO_FILES + base_name + '*')[0]

    print(audio_file)
    return render_template("index_new.html", 
                            sound_ids=sound_id,
                            page=page,
                            audio_file=audio_file,
                            loop_name=loop_name,
                            description=description,
                            tags=tags_to_display,
                            sound_image=sound_image,
                            guessedBPM=guessed_BPM,
                            guessedKey=guessed_Key,
                            guessedMode=guessedMode,
                            genres=["Pop","Rock","House"])


if __name__ == '__main__':
    app.run()
