from flask import Flask, render_template, request
import json


app = Flask(__name__, static_url_path='/static')

NUM_SOUNDS_PER_PAGE = 2


@app.route('/', methods = ['GET', 'POST'])
def annotator():
    if request.method == 'POST':
        # save annotations to json file
        data = request.get_json()
        json.dump(data['answers'], open('annotations/page-{}.json'.format(data['page']), 'w'))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    page = int(request.args.get('p', 1))
    all_sound_ids = json.load(open('static/example_sounds.json'))

    # get a chunk of sounds according to the requested page number
    sound_ids = all_sound_ids[(page-1)*NUM_SOUNDS_PER_PAGE:page*NUM_SOUNDS_PER_PAGE]

    return render_template("index.html", sound_ids=sound_ids, page=page)


if __name__ == '__main__':
    app.run()
