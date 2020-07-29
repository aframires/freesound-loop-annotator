# Freesound Loop Dataset Benchmarking Results

In this page, we present the full results of the benchmarking for the Freesound Loop Dataset.

## Tempo Estimation

### Various Annotations - Different

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 84.84 | 74.33 | 94.40 | 84.52 |
| Percival14 | 84.15 | 73.64 | 94.92 | 84.24 |
| Zapata14 | 83.81 | 60.29 | 90.70 | 78.27 |
| Degara12 | 83.55 | 61.41 | 90.18 | 78.38 |
| Bock15 | 69.34 | 50.39 | 91.73 | 70.49 |
| Bock15ACF | 75.37 | 54.01 | 91.56 | 73.64 |
| Bock15DBN | 64.94 | 49.35 | 94.75 | 69.68 |

### Various Annotations - Same

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 63.79 | 53.54 | 80.65 | 66.00 |
| Percival14 | 63.31 | 53.26 | 81.61 | 66.06 |
| Zapata14 | 62.84 | 40.71 | 73.56 | 59.04 |
| Degara12 | 62.45 | 41.48 | 72.70 | 58.88 |
| Bock15 | 47.41 | 33.05 | 77.30 | 52.59 |
| Bock15ACF | 54.02 | 35.63 | 75.57 | 55.08 |
| Bock15DBN | 44.35 | 32.09 | 79.50 | 51.98 |

### Single Annotations

| Algorithm | Accuracy1 | Accuracy1e | Accuracy2 | Mean Accuracy |
| ---- | ---- | ---- | ---- | ---- |
| Percival14_essentia | 57.45 | 45.80 | 80.22 | 61.16 |
| Percival14 | 57.18 | 47.43 | 79.13 | 61.25 |
| Zapata14 | 59.89 | 36.86 | 74.25 | 57.00 |
| Degara12 | 58.54 | 38.48 | 72.09 | 56.37 |
| Bock15 | 52.30 | 29.81 | 76.69 | 52.94 |
| Bock15ACF | 52.30 | 29.27 | 72.36 | 51.31 |
| Bock15DBN | 45.80 | 30.08 | 78.05 | 51.31 |

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

### Various Annotations - Different

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 93.72 | 2.09 | 1.83 | 1.57 | 95.63 |
| EdmkeyKrumhansl | 89.01 | 5.50 | 1.31 | 2.88 | 92.72 |
| EdmkeyTemperley | 81.68 | 2.62 | 7.33 | 3.40 | 85.86 |
| EdmkeyShaath | 93.72 | 2.09 | 1.83 | 1.57 | 95.63 |
| EssentiaBasic | 90.05 | 1.57 | 1.83 | 3.14 | 92.02 |
| QMULKeyDetector | 51.83 | 4.97 | 8.38 | 12.30 | 59.29 |

### Various Annotations - Same

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 84.70 | 4.98 | 0.71 | 6.05 | 88.61 |
| EdmkeyKrumhansl | 79.00 | 8.54 | 0.36 | 7.47 | 84.88 |
| EdmkeyTemperley | 67.97 | 2.14 | 9.25 | 1.07 | 72.03 |
| EdmkeyShaath | 84.70 | 4.98 | 0.71 | 6.05 | 88.61 |
| EssentiaBasic | 86.48 | 2.14 | 1.07 | 4.27 | 88.72 |
| QMULKeyDetector | 35.94 | 5.69 | 5.34 | 10.32 | 42.46 |

### Single Annotations

| Algorithm | Same | Fifth | Relative | Parallel | Mirex |
| ---- | ---- | ---- | ---- | ---- | ---- |
| Edmkey | 67.06 | 4.12 | 2.94 | 16.47 | 73.29 |
| EdmkeyKrumhansl | 59.41 | 7.65 | 1.76 | 17.65 | 67.29 |
| EdmkeyTemperley | 52.35 | 4.12 | 4.71 | 11.18 | 58.06 |
| EdmkeyShaath | 67.06 | 4.12 | 2.94 | 16.47 | 73.29 |
| EssentiaBasic | 70.59 | 2.94 | 2.94 | 11.18 | 75.18 |
| QMULKeyDetector | 28.24 | 5.29 | 3.53 | 17.65 | 35.47 |
