# FaceTrust Cross-dataset Evaluation

- Generated at: `2026-07-17T11:10:31+07:00`
- Detector backend: `ms-eff-gcvit-b0-ffpp+adaptive-torch-efficientnet_b0`
- Protocol: `deterministic coverage, up to 100 frames per class`
- Demo-source frames are excluded from DeepFake Facial.
- An `uncertain` output is counted as incorrect in strict accuracy.
- Frame-level samples may be correlated when extracted from the same video.

## Results by dataset

| Dataset | N | Strict accuracy | Balanced accuracy | Fake recall | Real recall | Uncertain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepFake Facial | 200 | 46.0% | 46.0% | 56.0% | 36.0% | 5.0% |
| Celeb-DF-v2 sample | 200 | 66.5% | 66.5% | 96.0% | 37.0% | 1.0% |
| **Combined** | **400** | **56.2%** | **56.2%** | **76.0%** | **36.5%** | **3.0%** |

## Combined confusion matrix

| Ground truth | Predicted fake | Predicted real | Uncertain |
| --- | ---: | ---: | ---: |
| Fake | 152 | 41 | 7 |
| Real | 122 | 73 | 5 |

## Interpretation

Strict accuracy is the fraction of all frames whose final label exactly matches ground truth. Balanced accuracy is the mean of fake recall and real recall, so the two classes contribute equally.
The fake risk index and decision margin are internal decision scores, not calibrated probabilities that a verdict is correct.
These results measure cross-domain generalization of the deployed checkpoint. They do not inherit the much higher same-dataset accuracy published by the model author.

## Per-dataset confusion matrices

### DeepFake Facial

| Ground truth | Predicted fake | Predicted real | Uncertain |
| --- | ---: | ---: | ---: |
| Fake | 56 | 38 | 6 |
| Real | 60 | 36 | 4 |

### Celeb-DF-v2 sample

| Ground truth | Predicted fake | Predicted real | Uncertain |
| --- | ---: | ---: | ---: |
| Fake | 96 | 3 | 1 |
| Real | 62 | 37 | 1 |
