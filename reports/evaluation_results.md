# FaceTrust Evaluation Results

- Generated at: `2026-07-17T11:13:05+07:00`
- Image directory: `data\demo-images`
- Total images: `18`

## Summary Metrics

| Metric | Value |
| --- | ---: |
| Accuracy | 100.0% |
| Fake precision | 100.0% |
| Fake recall | 100.0% |
| Fake F1 | 100.0% |
| Real precision | 100.0% |
| Real recall | 100.0% |
| Real F1 | 100.0% |
| Uncertain rate | 0.0% |
| Face detection rate | 100.0% |
| API success rate | 100.0% |

## Confusion Matrix

| Ground truth | Correct class | Wrong/uncertain |
| --- | ---: | ---: |
| Fake | 9 | 0 |
| Real | 9 | 0 |

## Pipeline Timing

| Timing | Milliseconds |
| --- | ---: |
| Mean | 2576.9 |
| Median | 524.0 |
| P95 | 1187.9 |
| Max | 36794.8 |

## Per-image Results

| File | Expected | Predicted | Correct | Risk | Margin | Face | Latency ms |
| --- | --- | --- | --- | ---: | ---: | --- | ---: |
| 001_barack-obama.jpg | real | real | yes | 0.1% | 99.8% | yes | 36794.8 |
| 002_portrait-01.jpg | fake | fake | yes | 79.7% | 98.9% | yes | 510.7 |
| 003_donald-trump.jpg | real | real | yes | 0.1% | 99.9% | yes | 642.3 |
| 004_portrait-02.jpg | fake | fake | yes | 79.9% | 99.8% | yes | 438.3 |
| 009_cristiano-ronaldo.jpg | real | real | yes | 3.6% | 92.8% | yes | 553.8 |
| 010_portrait-03.jpg | fake | fake | yes | 79.0% | 96.6% | yes | 370.5 |
| 011_lionel-messi.jpg | real | real | yes | 0.1% | 99.9% | yes | 446.8 |
| 012_portrait-04.jpg | fake | fake | yes | 79.4% | 98.0% | yes | 332.0 |
| 013_bill-gates.jpg | real | real | yes | 0.2% | 99.7% | yes | 407.9 |
| 014_portrait-05.jpg | fake | fake | yes | 67.8% | 59.3% | yes | 381.2 |
| 015_mark-zuckerberg.jpg | real | real | yes | 1.2% | 97.5% | yes | 874.7 |
| 016_portrait-06.jpg | fake | fake | yes | 75.7% | 85.7% | yes | 462.0 |
| 017_joe-biden.jpg | real | real | yes | 0.1% | 99.8% | yes | 612.0 |
| 018_portrait-07.jpg | fake | fake | yes | 79.6% | 98.7% | yes | 584.1 |
| 021_volodymyr-zelenskyy.jpg | real | real | yes | 0.1% | 99.8% | yes | 769.3 |
| 022_portrait-08.jpg | fake | fake | yes | 78.6% | 95.5% | yes | 478.8 |
| 023_tom-cruise.jpg | real | real | yes | 0.1% | 99.8% | yes | 537.4 |
| 024_spiderman.png | fake | fake | yes | 58.8% | 29.3% | yes | 1187.9 |

## Interpretation

This report evaluates the current deployed upload pipeline on the curated public-figure stress set.
The pipeline API completed 100.0% of requests and detected faces in 100.0% of images.
Model-level accuracy on this set is 100.0%; fake recall is 100.0%.
The decision margin is distance from the active threshold, not a calibrated probability that the verdict is correct.
This is useful evidence for the report: the system is operational end-to-end, while the model needs further cross-domain fine-tuning before being claimed as production-grade.
For a stronger thesis-grade result, add a larger held-out split containing face-swap, reenactment, diffusion-generated portraits, compressed social-media images, and real celebrity/public-figure photos.
