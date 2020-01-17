# percussive-annotator

The Loop Annotator is a Flask web application that is meant to run locally in your computer.
It is an annotation tool that was created for building a dataset of loops from Freesound.


# How to

Insall dependencies:
```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Download the FSL10k.zip file from the Shared Google Drive to the loop-annotator/static folder and unzip.

Start server:
`python app.py`

With GOOGLE CHROME go to:
`http://localhost:5000/?p=1`

Annotate and submit your answers.

Please check the genre taxonomy provided in [here](https://docs.google.com/document/d/1Rj8mSoDewvnmrTs8HK2yRJ4AgUUf7Ft-JW2xN_bd6P4/edit?usp=sharing) to familiarise yourself on how to annotate genres.

The annotations are stored using JSON files saved inside the `annotations/` directory.
