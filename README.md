# ScreenshotGenerator
This project aims to automate the selection of video screenshots. It employs `ffmpeg` to generate a pool of screenshots then calls on two `autogluon` machine learning models to score the  screenshots in order to select the best of them. The first model attempts to determine whether a screenshot is focused while the second model attempts to determine whether the screenshot is a portrait. The first model's score makes up 75% of the total score while the second model's score makes up 25% of the total score.

## Dependencies
The following must be installed on your system:
- [ffmpeg](https://ffmpeg.org/download.html)
- [MediaInfo](https://mediaarea.net/en/MediaInfo)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist) (if you're on Windows)

All Python dependencies are installed by running `pip install --user -U -r requirements.txt` in the project directory.

## Usage
Download [model.zip](https://drive.google.com/file/d/1oRFO0fW-fmFn-CfsdvQqNTqQgU2gaQ0B/view?usp=sharing) and extract the contents into the project directory then run something like the following:
```
python generate.py --screenshot-directory "B:\Screenshots" --video-path "Z:\Encodes\A Great Movie (2023).mkv"
```

Full set of options:
```
Usage: generate.py [OPTIONS]

Options:
  --ffmpeg-path TEXT           The path to ffmpeg. Defaults to 'ffmpeg', which requires ffmpeg to be in your path.
  --pool-directory TEXT        The directory in which to store the screenshot pool. Defaults to the temp directory.
  --pool-report-path TEXT      A text file listing all pool files in order of descending score. Defaults to not generating the report.
  --pool-size INTEGER          The size of the pool from which to select screenshots. Defaults to 64.
  --screenshot-count INTEGER   The number of screenshots to generate. Defaults to 4.
  --screenshot-directory TEXT  The directory in which to store the screenshots.  [required]
  --video-path TEXT            The path to the video for which to generate screenshots.  [required]
  --help                       Show this message and exit.
```

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
  --focused-directory TEXT       The directory containing training images for the focused model, organized into 'Yes' and 'No' subdirectories.  [required]
  --portrait-directory TEXT      The directory containing training images for the portrait model, organized into 'Yes' and 'No' subdirectories.  [required]
  --training-time-limit INTEGER  The training time limit (seconds). Defaults to letting autogluon run until it's had enough.
  --help                         Show this message and exit.
```