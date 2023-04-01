from .portrait_preference import PortraitPreference
from pathlib import Path
from platformdirs import user_data_dir
from tempfile import gettempdir

class Defaults:
    END_TIME = None
    FFMPEG_PATH = "ffmpeg"
    MODELS_DIRECTORY = str(Path(user_data_dir(appauthor=False, appname="screenshotgenerator"), "models"))
    POOL_DIRECTORY = gettempdir()
    POOL_SIZE = 64
    PORTRAIT_PREFERENCE = PortraitPreference.PORTRAIT
    SCREENSHOT_COUNT = 4
    SILENT = False
    START_TIME = "00:00:00"
    TIME_FORMAT = "%H:%M:%S"