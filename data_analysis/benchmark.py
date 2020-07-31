import json
import os


from audiocommons_ffont.key_estimation.evaluation_metrics import *
from audiocommons_ffont.tempo_estimation.evaluation_metrics import *

import numpy as np

ANNOTATIONS_FILE = "./annotation_dict.json"
FSL10K_PATH = "/mnt/f/code/research/freesound-loop-annotator/static/FSL10K/"
METADATA_FILE = os.path.join(FSL10K_PATH,"metadata.json")
AUDIO_FILE = os.path.join(FSL10K_PATH, "audio/wav/")
BENCHMARK_PATH = os.path.join(FSL10K_PATH,"benchmarking/")

def get_annotations():
    with open(ANNOTATIONS_FILE, "r") as ann_file:
        annotations = json.load(ann_file)    
    return annotations

def evaluate_user_annotations(annotations,strong_aggreement=False):
    with open(METADATA_FILE, "r") as md_file:
        md = json.load(md_file) 

    same_tempo_count = 0
    different_tempo_count = 0

    for sound_id in annotations:
        if strong_aggreement:
            same_tempo = 0
            for annotation in annotations[sound_id]:
                try:
                    if float(annotation["bpm"]) == md[sound_id]["annotations"]["bpm"]:
                        same_tempo +=1
                except Exception as e:
                    continue
            if same_tempo == len(annotations[sound_id]):
                same_tempo_count+=1
            else:
                different_tempo_count+=1            
        else:
            same_tempo = False
            for annotation in annotations[sound_id]:
                try:
                    if float(annotation["bpm"]) == md[sound_id]["annotations"]["bpm"]:
                        same_tempo = True
                except Exception as e:
                    continue
            if same_tempo == True:
                same_tempo_count+=1
            else:
                different_tempo_count+=1
        
    total = same_tempo_count + different_tempo_count         
               
    print(str(same_tempo_count) + " of " + str(total) + " have the same tempo as the one provided by the uploader")
    print(str(different_tempo_count) + " of " + str(total) + " have a different tempo than the one provided by the uploader")
    print(str(100*same_tempo_count/total) + "%% of the sounds have the same tempo as the one provided by the uploader")
    print(str(100*different_tempo_count/total) + "%% of the sounds have a different tempo than the one provided by the uploader")

def plot_tempo_dist(annotations):
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    from collections import Counter

    all_tempos = []
    same_tempos = []
    for sound_id in annotations:
        #Compile all annotations for all loops
        for annotation in annotations[sound_id]:
            try:
                all_tempos.append(float(annotation["bpm"]))
            except Exception as e:
                continue
        #If there are two annotations for the loop
        if len(annotations[sound_id]) == 2:
            if annotations[sound_id][0]["bpm"] == annotations[sound_id][1]["bpm"]:
                try:
                    same_tempos.append(float(annotations[sound_id][0]["bpm"]))
                except Exception as e:
                    continue
        #If there is only one annotation for the loop
        else:
            try:
                same_tempos.append(float(annotations[sound_id][0]["bpm"]))
            except Exception as e:
                continue
    min_tempo = 30
    max_tempo = 300
    plt.figure(figsize=(8,4))
    fig = plt.hist(all_tempos, bins=max_tempo-min_tempo, range=(min_tempo,max_tempo),  label="Histogram of all tempo annotations")
    plt.xticks(ticks=range(min_tempo,max_tempo,10),rotation='vertical') 

    plt.savefig('histogram_all_tempo.pdf',bbox_inches='tight')
    plt.clf()
    plt.hist(same_tempos,  bins=max_tempo-min_tempo, range=(min_tempo,max_tempo),  label="Histogram of just the matching tempo annotations")        
    plt.xticks(ticks=range(min_tempo,max_tempo,10), rotation='vertical') 
    plt.savefig('histogram_same_tempo.png')
    plt.clf()

    print(Counter(same_tempos))

    return None

def plot_key_dist(annotations):
    import matplotlib.pyplot as plt
    from collections import Counter

    all_keys = []
    same_keys = []
    all_modes = []
    same_modes = []
    all_keys_modes = []
    same_keys_modes = []
    for sound_id in annotations:
        #Collect all annotations of key and mode
        for annotation in annotations[sound_id]:

            all_keys.append(annotation["key"])
            all_modes.append(annotation["mode"])
            all_keys_modes.append(annotation["key"] + " " + annotation["mode"])

        #If there are two annotations for the loop
        if len(annotations[sound_id]) == 2:
            if annotations[sound_id][0]["key"] == annotations[sound_id][1]["key"]:
                same_keys.append(annotations[sound_id][0]["key"])
            if annotations[sound_id][0]["mode"] == annotations[sound_id][1]["mode"]:
                same_modes.append(annotations[sound_id][0]["mode"])
            if annotations[sound_id][0]["mode"] == annotations[sound_id][1]["mode"] and annotations[sound_id][0]["key"] == annotations[sound_id][1]["key"]:
                same_keys_modes.append(annotation["key"] + " " + annotation["mode"])

        else:
            same_keys.append(annotations[sound_id][0]["key"])
            same_keys.append(annotations[sound_id][0]["mode"])
            same_keys_modes.append(annotation["key"] + " " + annotation["mode"])

    for annotation in [all_keys, same_keys, all_modes, same_modes, all_keys_modes, same_keys_modes]:
        print(Counter(annotation))


    total = len(all_keys_modes)


    return all_keys_modes,same_keys_modes

def get_key_dist(annotations):
    from collections import Counter
    
    all_keys_modes = []
    for sound_id in annotations:
        for annotation in annotations[sound_id]:
            if annotation["key"] not in [None, "none","unknown"]:
               all_keys_modes.append(annotation["key"] + " " + annotation["mode"])

    count = Counter(all_keys_modes)
    total = len(all_keys_modes)

    print("& maj"+" & "+"min"+" & "+'none'+" & "+'unknown')
    for key in ["c","c#","d",'d#','e','f','f#','g','g#','a','a#','b']:
        print()
        print(key, end ="")
        for mode in ["maj","min",'none','unknown']:
            keymode = key + " " + mode
            print(" & "  + "{:.2%}".format(count[keymode]/total), end ="")








def plot_inst_dist(annotations):
    instrumentations = {"instrumentation_percussion":0,"instrumentation_bass":0,"instrumentation_chords":0,"instrumentation_melody":0,"instrumentation_fx":0,"instrumentation_vocal":0}
    count = 0
    count1 = 0
    count2 = 0
    for sound_id in annotations:
        #Compile all annotations for all loops
        if len(annotations[sound_id]) == 1:
            count1 = count1 + 1
        else:
            count2 = count2 + 1

        for annotation in annotations[sound_id]:
            count = count + 1
            for instrument in instrumentations.keys():
                if annotation[instrument] == 'True':
                    instrumentations[instrument] = instrumentations[instrument] + 1

    for instrument in instrumentations:
        print(instrument + " & {:.2%}".format(instrumentations[instrument]/count))

    print("N Sounds annotated:" + str(len(annotations)))
    print("N Annotations" + str(count))
    print("1ann" + str(count1))
    print("2ann" + str(count2))

def plt_genre_dist(annotations):
    genres = {"genre_bass_music":0,"genre_live_sounds":0,"genre_cinematic":0,"genre_global":0,"genre_hip_hop":0,"genre_house_techno":0,"genre_other_dance_music":0}
    count = 0
    for sound_id in annotations:
        #Compile all annotations for all loops
        for annotation in annotations[sound_id]:
            count = count + 1
            for gen in genres.keys():
                if annotation[gen] == 'True':
                    genres[gen] = genres[gen] + 1

    for gen in genres:
        print(gen + " & {:.2%}".format(genres[gen]/count))


def benchmark_tempo_annotations():
    from collections import defaultdict
    
    any_tempos1, any_tempos2, same_tempos, one_tempos, user_tempos = compile_tempo_annotations(get_annotations())  

    one_tempo = [same_tempos, one_tempos, user_tempos]
    one_tempo_names = ['Same Tempos', 'One Annotation Tempos', 'User Provided Tempos']

    analysis_algorithms = ['analysis_rhythm_essentia_basic','analysis_rhythm_gkiokas12','analysis_rhythm_madmom','analysis_rhythm_madmom_acf',
    'analysis_rhythm_madmom_dbn','analysis_rhythm_percival_essentia','analysis_rhythm_percival14','analysis_rhythm_percival14_mod']

    analysis_data = defaultdict(dict)
    for algorithm in analysis_algorithms:
        with open(os.path.join(BENCHMARK_PATH, algorithm+".json"),"r") as anly_file:
            analysis = json.load(anly_file)
            for sound_id in analysis:
                analysis_data[sound_id].update(analysis[sound_id])

    
    for idx, annotations in enumerate(one_tempo):
        data_for_eval = defaultdict(dict)
        
        for sound_id in annotations:
            try:
                data_for_eval[sound_id]["annotations"] = {"bpm": float(annotations[sound_id]["annotations"]["bpm"])}
                data_for_eval[sound_id]["analysis"] = analysis_data[sound_id]
            except Exception as ex:
                ex   
        algorithm_list = ['Percival14_essentia','Percival14','Zapata14','Degara12','Bock15','Bock15ACF','Bock15DBN',]
        print(one_tempo_names[idx])
        print("Algorithm & Accuracy1 & Accuracy1e & Accuracy2 & Mean Accuracy")
        for algorithm in algorithm_list:
            a1 = np.mean(accuracy1(data_for_eval,algorithm))*100
            a1e = np.mean(accuracy1e(data_for_eval,algorithm))*100
            a2 = np.mean(accuracy2(data_for_eval,algorithm))*100
            ma = np.mean([a1,a1e,a2])

            print(algorithm + " & " + "{:.2f}".format(a1) + " & " + "{:.2f}".format(a1e) +  " & " + "{:.2f}".format(a2) + " & " + "{:.2f}".format(ma))

    data_for_eval1 = defaultdict(dict)
    data_for_eval2 = defaultdict(dict)
    for sound_id in any_tempos1:
        try:
            data_for_eval1[sound_id]["annotations"] = {"bpm": float(any_tempos1[sound_id]["annotations"]["bpm"])}
            data_for_eval1[sound_id]["analysis"] = analysis_data[sound_id]
            data_for_eval2[sound_id]["annotations"] = {"bpm": float(any_tempos2[sound_id]["annotations"]["bpm"])}
            data_for_eval2[sound_id]["analysis"] = analysis_data[sound_id]
        except Exception as ex:
            ex   
    algorithm_list = ['Percival14_essentia','Percival14','Zapata14','Degara12','Bock15','Bock15ACF','Bock15DBN']
    print("Different Tempos")
    print("Algorithm & Accuracy1 & Accuracy1e & Accuracy2 & Mean Accuracy")
    for algorithm in algorithm_list:
        a1 = np.mean(list(map(max,accuracy1(data_for_eval1,algorithm),accuracy1(data_for_eval2,algorithm))))*100
        a1e = np.mean(list(map(max,accuracy1e(data_for_eval1,algorithm),accuracy1e(data_for_eval2,algorithm))))*100
        a2 = np.mean(list(map(max,accuracy2(data_for_eval1,algorithm),accuracy2(data_for_eval2,algorithm))))*100
        ma = np.mean([a1,a1e,a2])

        print(algorithm + " & " + "{:.2f}".format(a1) + " & " + "{:.2f}".format(a1e) +  " & " + "{:.2f}".format(a2) + " & " + "{:.2f}".format(ma))


def compile_tempo_annotations(annotations):
    from collections import defaultdict

    any_tempos1 = defaultdict(dict)
    any_tempos2 = defaultdict(dict)
    same_tempos = defaultdict(dict)
    one_tempos = defaultdict(dict)
    
    for sound_id in annotations:
        #If there are two annotations for the loop
        if len(annotations[sound_id]) == 2:
            if annotations[sound_id][0]["bpm"] == annotations[sound_id][1]["bpm"]:
                try:
                    same_tempos[sound_id]["annotations"] = {"bpm": annotations[sound_id][0]["bpm"]}
                    any_tempos1[sound_id]["annotations"] = {"bpm": annotations[sound_id][0]["bpm"]}
                    any_tempos2[sound_id]["annotations"] = {"bpm": annotations[sound_id][1]["bpm"]}
                except Exception as e:
                    print(e)
            else:
                try:
                    any_tempos1[sound_id]["annotations"] = {"bpm": annotations[sound_id][0]["bpm"]}
                    any_tempos2[sound_id]["annotations"] = {"bpm": annotations[sound_id][1]["bpm"]}
                except Exception as e:
                    print(e)
        #If there is only one annotation for the loop
        else:
            try:
                one_tempos[sound_id]["annotations"] = {"bpm": annotations[sound_id][0]["bpm"]}
            except Exception as e:
                print(e)

    with open(METADATA_FILE, "r") as md_file:
        user_tempos = json.load(md_file)


    return any_tempos1, any_tempos2, same_tempos, one_tempos, user_tempos     

def replace_key(key):
    keys_to_replace = ['C#','D#','F#','G#','A#']
    correct_keys = ['Db','Eb','Gb','Ab','Bb']
    if key in keys_to_replace:
        idx = keys_to_replace.index(key)
        return correct_keys[idx]
    else:
        return key

def replace_mode(mode):
    if mode == 'maj':
        return 'major'
    if mode == 'min':
        return 'minor'

def compile_key_annotations(annotations):
    from collections import defaultdict

    any_keys1 = defaultdict(dict)
    any_keys2 = defaultdict(dict)
    same_keys = defaultdict(dict)
    one_keys = defaultdict(dict)
    
    for sound_id in annotations:
        #If there are two annotations for the loop
        if len(annotations[sound_id]) == 2:
            if annotations[sound_id][0]["key"] == annotations[sound_id][1]["key"] and \
                annotations[sound_id][0]["mode"] == annotations[sound_id][1]["mode"]:
                if annotations[sound_id][0]["key"] != 'none' and annotations[sound_id][0]["mode"] != 'none' and \
                    annotations[sound_id][0]["key"] != 'unknown' and annotations[sound_id][0]["mode"] != 'unknown':
                    try:
                        same_keys[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][0]["key"]) + " " + replace_mode(annotations[sound_id][0]["mode"])}
                        any_keys1[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][0]["key"]) + " " + replace_mode(annotations[sound_id][0]["mode"])}
                        any_keys2[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][1]["key"]) + " " + replace_mode(annotations[sound_id][1]["mode"])}
                    except Exception as e:
                        print(e)
            else:
                try:
                    if annotations[sound_id][0]["key"] != 'none' and annotations[sound_id][1]["key"] != 'none' and \
                        annotations[sound_id][0]["mode"] != 'none' and annotations[sound_id][1]["mode"] != 'none' and \
                          annotations[sound_id][0]["key"] != 'unknown' and annotations[sound_id][0]["mode"] != 'unknown'and \
                            annotations[sound_id][1]["key"] != 'unknown' and annotations[sound_id][1]["mode"] != 'unknown'  :

                        any_keys1[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][0]["key"]) + " " + replace_mode(annotations[sound_id][0]["mode"])}
                        any_keys2[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][1]["key"]) + " " + replace_mode(annotations[sound_id][1]["mode"])}
                except Exception as e:
                    e
        #If there is only one annotation for the loop
        else:
            try:
                if annotations[sound_id][0]["key"] != 'none' and annotations[sound_id][0]["mode"] != 'none' and \
                    annotations[sound_id][0]["key"] != 'unknown' and annotations[sound_id][0]["mode"] != 'unknown':
                    one_keys[sound_id]["annotations"] = {"key": replace_key(annotations[sound_id][0]["key"]) + " " + replace_mode(annotations[sound_id][0]["mode"])}
            except Exception as e:
                e


    return any_keys1, any_keys2, same_keys, one_keys    

    
    

def benchmark_key_annotations():
    from collections import defaultdict
    
    any_keys1, any_keys2, same_keys, one_keys = compile_key_annotations(get_annotations())  

    one_key = [same_keys, one_keys]
    one_key_names = ['Same Keys', 'One Annotation Keys']

    analysis_algorithms = ['analysis_tonal_qmul_key_detector','analysis_tonal_key_essentia_basic','analysis_tonal_edmkey']

    analysis_data = defaultdict(dict)
    for algorithm in analysis_algorithms:
        with open(os.path.join(BENCHMARK_PATH, algorithm+".json"),"r") as anly_file:
            analysis = json.load(anly_file)
            for sound_id in analysis:
                analysis_data[sound_id].update(analysis[sound_id])

    
    for idx, annotations in enumerate(one_key):
        data_for_eval = defaultdict(dict)
        
        for sound_id in annotations:
            try:
                data_for_eval[sound_id]["annotations"] = {"key": annotations[sound_id]["annotations"]["key"]}
                data_for_eval[sound_id]["analysis"] = analysis_data[sound_id]
            except Exception as ex:
                print(ex)    
        algorithm_list = ["Edmkey","EdmkeyKrumhansl","EdmkeyTemperley","EdmkeyShaath","EssentiaBasic","QMULKeyDetector"]
        print(one_key_names[idx])
        print("Algorithm & Same & Fifth & Relative & Parallel & Mirex")
        for algorithm in algorithm_list:
            same = np.mean(mireval_key_same(data_for_eval,algorithm))*100
            fifth = np.mean(mireval_key_fifth(data_for_eval,algorithm))*100
            relative = np.mean(mireval_key_relative(data_for_eval,algorithm))*100
            parallel = np.mean(mireval_key_parallel(data_for_eval,algorithm))*100
            mirex = same + 0.5*fifth + 0.3*relative + 0.2*parallel

            print(algorithm + " & " + "{:.2f}".format(same) + " & " + "{:.2f}".format(fifth) +  " & " + "{:.2f}".format(relative) + " & " + "{:.2f}".format(parallel) + " & " + "{:.2f}".format(mirex))

    data_for_eval1 = defaultdict(dict)
    data_for_eval2 = defaultdict(dict)
    keys = set(any_keys1.keys())
    keys.update(any_keys2.keys())
    for sound_id in keys:
        try:
            data_for_eval1[sound_id]["annotations"] = {"key": any_keys1[sound_id]["annotations"]["key"]}
            data_for_eval1[sound_id]["analysis"] = analysis_data[sound_id]
            data_for_eval2[sound_id]["annotations"] = {"key": any_keys2[sound_id]["annotations"]["key"]}
            data_for_eval2[sound_id]["analysis"] = analysis_data[sound_id]
        except Exception as ex:
            print(ex)    
    print("Different Keys")
    print("Algorithm & Same & Fifth & Relative & Parallel & Mirex")
    for algorithm in algorithm_list:
        max_accuracies = list(map(max,mireval_key_same(data_for_eval1,algorithm),mireval_key_same(data_for_eval2,algorithm), \
            [0.5 * x for x in mireval_key_fifth(data_for_eval1,algorithm)], [0.5 * x for x in mireval_key_fifth(data_for_eval2,algorithm)], \
            [0.3 * x for x in mireval_key_relative(data_for_eval1,algorithm)], [0.3 * x for x in mireval_key_relative(data_for_eval2,algorithm)], \
            [0.2 * x for x in mireval_key_parallel(data_for_eval1,algorithm)], [0.2 * x for x in mireval_key_parallel(data_for_eval2,algorithm)]))






        same = (max_accuracies.count(1)/len(max_accuracies))*100
        fifth = (max_accuracies.count(0.5)/len(max_accuracies))*100
        relative = (max_accuracies.count(0.3)/len(max_accuracies))*100
        parallel = (max_accuracies.count(0.2)/len(max_accuracies))*100
        mirex = 100 * sum(max_accuracies)/len(max_accuracies) 
        print(algorithm + " & " + "{:.2f}".format(same) + " & " + "{:.2f}".format(fifth) +  " & " + "{:.2f}".format(relative) + " & " + "{:.2f}".format(parallel) + " & " + "{:.2f}".format(mirex))
        #print(algorithm + " & " + "{:.2f}".format(same) + " & " + "{:.2f}".format(fifth) +  " & " + "{:.2f}".format(relative) + " & " + "{:.2f}".format(parallel) + " & " + "{:.2f}".format(mirex))


def get_loops_with_tempo(tempo,annotations):
    from shutil import copyfile

    dest_dir = "./jordan_loops/"
    tempo_annotations = {}
    ids_to_move = []
    for sound_id in annotations:
        #If there are two annotations for the loop
        if len(annotations[sound_id]) == 2:
            if annotations[sound_id][0]["bpm"] == annotations[sound_id][1]["bpm"]:
                try:
                    if annotations[sound_id][0]["bpm"] == "120":
                        tempo_annotations[sound_id] = annotations[sound_id]
                        ids_to_move.append(sound_id)
                except Exception as e:
                    continue
        #If there is only one annotation for the loop
        else:
            try:
                if annotations[sound_id][0]["bpm"] == "120":
                    tempo_annotations[sound_id] = annotations[sound_id]
                    ids_to_move.append(sound_id)
            except Exception as e:
                continue
    
    with open('jordan_loops.json', 'w') as filehandle:
        json.dump(tempo_annotations, filehandle)


    for sound_id in ids_to_move:
        for root, subdirs, files in os.walk(AUDIO_FILE):
            for filename in files:
                if sound_id + "_" in filename:
                    copyfile(os.path.join(AUDIO_FILE, filename),os.path.join(dest_dir,filename))
                    
plot_inst_dist(get_annotations())
get_key_dist(get_annotations())
plt_genre_dist(get_annotations())
plot_tempo_dist(get_annotations())


print("Weak Agreement (if the estimation matches one of the annotations)")
evaluate_user_annotations(get_annotations(),False)
print()
print("Strong Agreement (if the estimation matches both of the annotations)")
evaluate_user_annotations(get_annotations(),True)


benchmark_tempo_annotations()
benchmark_key_annotations()

