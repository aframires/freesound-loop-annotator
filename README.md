# Freesound Loop Annotator

The Loop Annotator is a Flask web application that is meant to run locally in your computer.
It is an annotation tool that was created for building a dataset of loops from Freesound.

This app is hosted online and accessible at https://mtg.upf.edu/fslannotator/

The full dataset can be found in https://zenodo.org/record/3967852

The full paper is available at https://arxiv.org/abs/2008.11507 and extra results and examples are provided at https://aframires.github.io/freesound-loop-annotator/

If you use this work for research, please cite:

```@inproceedings{ramires2020, author = "Antonio Ramires and Frederic Font and Dmitry Bogdanov and Jordan B. L. Smith and Yi-Hsuan Yang and Joann Ching and Bo-Yu Chen and Yueh-Kao Wu and Hsu Wei-Han and Xavier Serra", title = "The Freesound Loop Dataset and Annotation Tool", booktitle = "Proc. of the 21st International Society for Music Information Retrieval (ISMIR)", year = "2020" }```

# How to run locally

This application runs inside a docker container. To run the app you simply need to clone the repository and run docker compose:

```shell
git clone https://github.com/aframires/freesound-loop-annotator.git
cd freesound-loop-annotator
docker-compose up
```

Before doing that you'll need to download data files and edit `docker-compose.yml` so the correct data volume is mounted.
Download corresponding zip file with the actual audio files from the Shared Google Drive as per the email instructions. Copy the file to the `static` folder and unzip. Rename the unzipped folder to `FSL10K` (if it is not already named like that). You should now have a directory structure like `static/FSL10K/audio`, `static/FSL10K/ac_analysis`, etc. You can now remove the downloaded `.zip` file.

Now start docker:
`docker-compose up`

Use Google Chrome to navigate to this address:
`http://localhost:5000/fslannotator/`

You'll be presented with loops to annotate. Fill in all the fields and click "submit". This will save your annotations and automatically **move to the next loop**.

Reloading `http://localhost:5000/fslannotator/` will present you the last unnanotated loop, therefore you can safely close the browser at any time.

The annotations are stored using JSON files saved inside the `annotations/` inside the `FSL10K` folder mounted in the container. Once all sounds are annotated, zip the annotations directory and please send the file as per the email instructions.

Before annotating, please check the genre taxonomy provided in [here](https://docs.google.com/document/d/1Rj8mSoDewvnmrTs8HK2yRJ4AgUUf7Ft-JW2xN_bd6P4/edit?usp=sharing) to familiarise yourself on how to annotate genres.

# Running the Evaluation

In order to get the proposed benchmarks and evaluation metrics:
- Download the dataset from [Zenodo](https://zenodo.org/record/3967852) and add it inside the static folder of the directory.
- Run the [analyse_data.py](data_analysis/analyse_data.py) file to obtain the inter-annotator agreement.
- Run the [benchmark.py](data_analysis/benchmark.py) file to obtain the statistics of the dataset (key, tempo distribution) and the benchmarking values.
- Run the code provided in Jordan Smith's [repo](https://github.com/jblsmith/ismir2020-loops) to obtain the music generation and decomposition evaluation.
