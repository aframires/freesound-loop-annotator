# percussive-annotator

The Loop Annotator is a Flask web application that is meant to run locally in your computer.
It is an annotation tool that was created for building a dataset of loops from Freesound.


# How to

Clone repository, insall dependencies:
```shell
git clone https://github.com/aframires/freesound-loop-annotator.git
cd freesound-loop-annotator
pip install -r requirements.txt  # or create a virtual environment to install them. it only requires flask anyway so you'll probably have it already
```

Download corresponding zip file with the actual audio files from the Shared Google Drive as per the email instructions. Copy the file to the `static` folder and unzip. Rename the unzipped folder to `FSL10K` (if it is not already named like that). You should now have a directory structure like `static/FSL10K/audio`, `static/FSL10K/ac_analysis`, etc. You can now remove the downloaded `.zip` file.

Now start the server (if you see "internal server error" make sure that the directory structure after adding the dada matches the description above):
`python app.py`

Use Google Chrome to navigate to this address:
`http://localhost:5000/`

You'll be presented with loops to annotate. Fill in all the fields and click "submit". This will save your annotations and automatically **move to the next loop**.

Reloading `http://localhost:5000/` will present you the last unnanotated loop, therefore you can safely close the browser at any time.

The annotations are stored using JSON files saved inside the `annotations/` directory. Once all sounds are annotated, zip the annotations directory and please send the file as per the email instructions.

Before annotating, please check the genre taxonomy provided in [here](https://docs.google.com/document/d/1Rj8mSoDewvnmrTs8HK2yRJ4AgUUf7Ft-JW2xN_bd6P4/edit?usp=sharing) to familiarise yourself on how to annotate genres.
