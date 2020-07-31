import os

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(os.path.expanduser("~"), 'Data/AudioCommons')
TEST_FILES_PATH = os.path.join(DATA_PATH, 'test_files')
TEMPO_ESTIMATION_OUT_PATH = os.path.join(PROJECT_PATH, 'tempo_estimation', 'out')
FREESOUND_EXTRACTOR_PATH_04 = os.path.join(PROJECT_PATH, 'extractors', 'essentia_streaming_extractor_freesound_04')
FREESOUND_EXTRACTOR_PATH_03 = os.path.join(PROJECT_PATH, 'extractors', 'essentia_streaming_extractor_freesound_03')

#from local_settings import *