# percussive-annotator

The Percussive Annotator is a Flask web application that is meant to run locally in your computer.
It is an annotation tool that was created for building a dataset of isolated single event percussive sounds.
The dataset is used for training a neural network synthesising percussive sounds.

More information coming soon!


# How to

Insall dependencies:
```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start server:
`python app.py`

With your browser go to:
`http://localhost:5000/?p=1`

Annotate and submit your answers.

The annotations are stored using JSON files saved inside the `annotations/` directory.
