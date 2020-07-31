# Freesound Loop Dataset Benchmarking Results

In this page, we present the full results of the benchmarking for the Freesound Loop Dataset.

## Tempo Estimation

For tempo estimation, we used the following metrics:
Accuracy 1 is the percentage of instances whose estimated BPM is within 4% of the annotated ground truth. 
Accuracy 2 is the percentage ofinstances whose estimated BPM is within a 4% of 1/3,1/2, 1, 2, or 3 times the ground truth BPM.
Accuracy 1e repre-sents the percentage of instances whose estimated BPM is exactly the same as the ground truth after rounding the estimated BPM to the nearest integer.

### Various Annotations - Either

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 84.39 | 73.81 | 94.18 | 84.13 |
| Percival14 | 85.24 | 73.39 | 96.31 | 84.98 |
| Zapata14 | 83.32 | 60.75 | 89.85 | 77.97 |
| Degara12 | 83.53 | 63.38 | 90.56 | 79.16 |
| Bock15 | 70.05 | 51.88 | 92.12 | 71.35 |
| Bock15ACF | 77.29 | 54.58 | 92.83 | 74.90 |
| Bock15DBN | 67.00 | 51.03 | 94.68 | 70.90 |

### Various Annotations - Same

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia |  63.55 | 53.18 | 80.52 | 65.75 |
| Percival14 | 62.92 | 52.32 | 81.23 | 65.49 |
| Zapata14 | 62.84 | 41.01 | 73.13 | 58.99 |
| Degara12 | 62.53 | 42.66 | 72.74 | 59.31 |
| Bock15 | 48.08 | 33.54 | 77.14 | 52.92 |
| Bock15ACF | 53.65 | 35.43 | 75.18 | 54.75 |
| Bock15DBN | 44.78 | 32.99 | 79.18 | 52.32 |

### Single Annotations

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 60.35 | 50.24 | 78.34 | 62.98 |
| Percival14 | 61.10 | 51.80 | 79.09 | 64.00 |
| Zapata14 | 62.39 | 40.46 | 73.52 | 58.79 |
| Degara12 | 62.25 | 41.00 | 73.05 | 58.77 |
| Bock15 | 50.64 | 27.56 | 75.29 | 51.17 |
| Bock15ACF | 52.68 | 31.77 | 71.42 | 51.96 |
| Bock15DBN | 44.81 | 29.60 | 77.39 | 50.60 |

### Automatic Annotations

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 56.73 | 46.56 | 70.98 | 58.09 |
| Percival14 | 56.01 | 45.80 | 71.65 | 57.82 |
| Zapata14 | 56.27 | 33.59 | 65.57 | 51.81 |
| Degara12 | 56.43 | 35.07 | 65.47 | 52.32 |
| Bock15 | 40.22 | 25.62 | 67.41 | 44.42 |
| Bock15ACF | 48.74 | 29.98 | 67.24 | 48.65 |
| Bock15DBN | 38.73 | 26.45 | 72.10 | 45.76 |

## Key Estimation

For key estimation, we use the MIREX metrics for the Audio Key Detection. These are described as:

> Keys will be considered as "close" if they have one of the following relationships: distance of perfect fifth, relative major and minor, and parallel major and minor. A correct key assignment will be given a full point, and incorrect assignments will be allocated fractions of a point according to the following table:

| Relation to Correct Key |	Points |
| Same 	| 1.0 |
| Perfect fifth | 0.5 |
| Relative major/minor | 0.3 |
| Parallel major/minor | 0.2 |
| Other | 0.0 |

> The points are counted over all files and averaged. The number of correctly identified keys as well as the distribution of the errors is also reported. 

### Various Annotations - Different

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 80.57 | 6.40 | 2.21 | 5.96 | 85.63 |
| EdmkeyKrumhansl | 76.60 | 9.27 | 1.10 | 7.06 | 82.98 |
| EdmkeyTemperley | 67.33 | 2.87 | 8.83 | 1.77 | 71.77 |
| EdmkeyShaath | 80.57 | 6.40 | 2.21 | 5.96 | 85.63 |
| EssentiaBasic | 82.12 | 3.09 | 2.65 | 4.19 | 85.30 |
| QMULKeyDetector | 39.07 | 6.62 | 5.96 | 10.38 | 46.25 |

### Various Annotations - Same

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 84.36 | 4.91 | 0.92 | 5.83 | 88.25 |
| EdmkeyKrumhansl | 79.45 | 7.67 | 0.31 | 7.36 | 84.85 |
| EdmkeyTemperley | 67.79 | 2.45 | 8.59 | 0.92 | 71.78 |
| EdmkeyShaath | 84.36 | 4.91 | 0.92 | 5.83 | 88.25 |
| EssentiaBasic | 86.50 | 2.15 | 1.23 | 4.29 | 88.80 |
| QMULKeyDetector | 35.28 | 5.52 | 5.52 | 12.27 | 42.15 |

### Single Annotations

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 66.24 | 5.44 | 3.20 | 11.68 | 72.26 |
| EdmkeyKrumhansl | 59.84 | 7.20 | 3.20 | 12.96 | 66.99 |
| EdmkeyTemperley | 56.32 | 3.52 | 6.88 | 6.56 | 61.46 |
| EdmkeyShaath | 66.40 | 5.44 | 3.20 | 11.52 | 72.38 |
| EssentiaBasic | 66.88 | 3.20 | 2.72 | 9.76 | 71.25 |
| QMULKeyDetector | 28.64 | 5.44 | 3.36 | 13.60 | 35.09 |

## Music Generation

In this section, we present example templates used for the generation of music pieces from loops, and some audio examples of the generated pieces.

### Example Layouts

![Example Layouts](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/layout_examples.png "Example layouts for music generation.")

### Music Examples
Sparse Layout
[Sparse1](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/act_1_0.mp3)
[Sparse2](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/act_1_1.mp3)

Dense Layout
[Dense1](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/act_2_0.mp3)
[Dense2](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/act_2_1.mp3)

Factorial Layout
[Factorial1](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/facto_0.mp3)
[Factorial2](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/facto_1.mp3)

Composed Layout
[Composed1](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/lopez_0.mp3)
[Composed2](https://github.com/aframires/freesound-loop-annotator/tree/master/docs/audios/lopez_1.mp3)

