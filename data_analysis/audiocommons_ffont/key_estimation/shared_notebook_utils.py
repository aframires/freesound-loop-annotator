import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath("__file__")), os.pardir))

import os
import sys
import IPython
import numpy as np
import matplotlib.pyplot as plt
import seaborn
import settings
import inspect
import random
import math
from ac_utils.general import *
from ac_utils.evaluation import *
from ac_utils.processing import *
from ac_utils.datasets import *
from ac_utils.sound import *
from ac_utils.plotting import *
from evaluation_metrics import *
from sklearn.externals import joblib

seaborn.set(style="whitegrid")


def condition_instance_acceptable(key, item, data):
    annotated_tonality = vfkp(item, 'annotations.key')
    if annotated_tonality:
        key, scale = annotated_tonality.split(' ')
        if scale not in ['major', 'minor']:
            return False
        if not key:
            return False
        return True
    return False


def load_datasets(dirnames=None, clean=False, exclude_files=None):
    if dirnames is None:
        raise Exception("No dataset directory names sepecified!")
    datasets = list()
    for dirname in dirnames:
        dataset = Dataset(dirname=dirname, exclude_files=exclude_files)
        if clean:
            dataset = dataset.filter_data(condition=condition_instance_acceptable)
        datasets.append(dataset)
    return datasets
