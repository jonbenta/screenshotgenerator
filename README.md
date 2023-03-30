# screenshotgenerator

## Usage
See the [PyPI project](https://pypi.org/project/screenshotgenerator/) for details.

## Contributing
More training data means better the model accuracy (in theory). However, my ability to curate training data is limited. If you'd like to contribute, please upload your curated files into the [appropriate subdirectories](https://drive.google.com/drive/folders/1LW7msqJ2T2KSFQoxo_CJ2tpRrIk3PIxP?usp=share_link).

## Training
Not happy with my models? Think you can do better? Great! You can train your own models with `training/train.py`:

```
Usage: train.py [OPTIONS]

Options:
  --focused-training-data-directory TEXT
                                  The directory containing training images for
                                  the focused model, organized into 'Yes' and
                                  'No' subdirectories.  [required]
  --models-directory TEXT         The directory in which to store the models.
                                  [required]
  --portrait-training-data-directory TEXT
                                  The directory containing training images for
                                  the portrait model, organized into 'Yes' and
                                  'No' subdirectories.  [required]
  --training-time-limit INTEGER   The training time limit (seconds). Defaults
                                  to letting autogluon run until it's had
                                  enough.
  --help                          Show this message and exit.
```

### Dependencies
[Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist) is required, if you are on Windows.

#### CUDA
`autogluon` uses the CPU version of PyTorch, by default. If you have a CUDA-enabled GPU, installing the CUDA version of PyTorch will greatly increase training speed:
```
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
```