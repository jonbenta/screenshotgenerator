# ScreenshotGenerator
This project aims to automate the selection of video screenshots. It employs `ffmpeg` to generate a pool of screenshots then calls on two `autogluon` machine learning models to score the screenshots in order to select the best of them. The first model attempts to determine whether a screenshot is focused while the second model attempts to determine whether the screenshot is a portrait (a close-up of one or more people). The first model's score makes up 75% of the total score while the second model's score makes up 25% of the total score.

## Dependencies
The following must be installed on your system:
- [ffmpeg](https://ffmpeg.org/download.html)
- [MediaInfo](https://mediaarea.net/en/MediaInfo)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist) (if you're on Windows)

All Python dependencies are installed by running `pip install --user -U -r requirements.txt` in the project directory.

### CUDA
`autogluon` uses the CPU version of PyTorch, by default. If you have a CUDA-enabled GPU, installing the CUDA version of PyTorch will increase prediction and training speeds:
```
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
```

## Usage

### CLI
Download [models.zip](https://drive.google.com/file/d/1oRFO0fW-fmFn-CfsdvQqNTqQgU2gaQ0B/view?usp=sharing) and extract the contents into the project directory then run something like the following:
```
python generate.py --screenshot-directory "B:\Screenshots" --video-path "Z:\Encodes\A Great Movie (2023).mkv"
```

Full set of options:
```
Usage: generate.py [OPTIONS]

Options:
  --end-time [%H:%M:%S]           The time at which to stop taking
                                  screenshots. Defaults to 95% of the video
                                  duration, to exclude credits.
  --ffmpeg-path TEXT              The path to ffmpeg.  [default: ffmpeg]
  --pool-directory TEXT           The directory in which to store the
                                  screenshot pool. Defaults to the 
                                  temporary directory.
  --pool-report-path TEXT         A JSON file detailing the screenshot pool,
                                  sorted by descending preference.
  --pool-size INTEGER             The size of the pool from which to select
                                  screenshots.  [default: 64]
  --portrait-preference [mixed|noportrait|portrait]
                                  Preference regarding portrait screenshots.
                                  [default: portrait]
  --screenshot-count INTEGER      The number of screenshots to select.
                                  [default: 4]
  --screenshot-directory TEXT     The directory into which to copy the
                                  selected screenshots.  [required]
  --silent                        Suppress ffmpeg and autogluon output.
  --start-time [%H:%M:%S]         The time at which to start taking
                                  screenshots.  [default: 00:00:00]
  --video-path TEXT               The path to the video for which to generate
                                  screenshots.  [required]
  --help                          Show this message and exit.
```

### Library
The [screenshotgenerator](https://pypi.org/project/screenshotgenerator) package, published on PyPI, enables programmatic integration.

## Contributing
More training data means better the model accuracy (in theory). However, my ability to curate training data is limited. If you'd like to contribute, please upload your curated files into the appropriate subdirectories [here](https://drive.google.com/drive/folders/1LW7msqJ2T2KSFQoxo_CJ2tpRrIk3PIxP?usp=share_link).

## Training
Not happy with my models? Think you can do better? Great! You can train your own models by running something like the following:
```
python train.py --focused-directory "B:\Focused Training Data" --portrait-directory "B:\Portrait Training Data"
```

Full set of options:
```
Usage: train.py [OPTIONS]

Options:
  --focused-directory TEXT       The directory containing training images for
                                 the focused model, organized into 'Yes' and
                                 'No' subdirectories.  [required]
  --portrait-directory TEXT      The directory containing training images for
                                 the portrait model, organized into 'Yes' and
                                 'No' subdirectories.  [required]
  --training-time-limit INTEGER  The training time limit (seconds). Defaults
                                 to letting autogluon run until it's had
                                 enough.
  --help                         Show this message and exit.
```
