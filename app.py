from flask import Flask, render_template, request
import json


app = Flask(__name__, static_url_path='/static')


PATH_TO_FILE_WITH_SOUND_IDS = 'F:\\Code\\Data\\Loops\\FSL10k\\metadata_sound_ids_list.json'
PATH_TO_AC_ANALYSIS = 'F:\\Code\\Data\\Loops\\FSL10k\\ac_analysis\\'
PATH_TO_METADATA = 'F:\\Code\\Data\\Loops\\FSL10k\\fs_analysis\\'
PATH_TO_AUDIO_FILES = 'F:\\Code\\Data\\Loops\\FSL10k\\audio\\original\\'

def find_genre_tags(tags):
    return

def find_instruments_tags(tags):
    return


@app.route('/', methods = ['GET', 'POST'])
def annotator():
    if request.method == 'POST':
        # save annotations to json file
        data = request.get_json()
        json.dump(data['answers'], open('annotations/page-{}.json'.format(data['page']), 'w'))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    page = int(request.args.get('p', 1))
    sound_ids = json.load(open(PATH_TO_FILE_WITH_SOUND_IDS, 'rb'))

    # get a chunk of sounds according to the requested page number
    sound_id = all_sound_ids[(page-1)]
    metadata = json.load(open(PATH_TO_METADATA + sound_id + '.json', 'rb'))
    loop_name = metadata["name"]
    sound_image = metadata["image"]
    description = metadata["description"]
    
    tags = metadata["tags"]
    tags_to_display = ', '.join(tags)
    
    #instruments = find_instruments_tags(tags)
    guessed_BPM = metadata["annotations"]["bpm"]

    ac_analysis_filename = metadata["preview_url"]
    ac_analysis_filename = ac_analysis_filename[ac_analysis_filename.find("previews/*/"):ac_analysis_filename.find("-hq")] + "_analysis.json"
    ac_analysis = json.load(open(PATH_TO_AC_ANALYSIS + ac_analysis_filename, 'rb'))
    tonality = ac_analysis["tonality"]
    space_ind = tonality.find(' ')
    guessed_Key = tonality[0:space_ind-1]
    guessedMode = tonality[space_ind + 1:]
    #genres = find_genre_tags(tags)





    return render_template("index_new.html", 
                            sound_ids=sound_id,
                            page=page,
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
