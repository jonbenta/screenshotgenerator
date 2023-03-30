from .portrait_preference import PortraitPreference
from datetime import timedelta
from tempfile import gettempdir

class Defaults:
    END_TIME = None
    FFMPEG_PATH = "ffmpeg"
    POOL_DIRECTORY = gettempdir()
    POOL_SIZE = 64
    PORTRAIT_PREFERENCE = PortraitPreference.PORTRAIT
    SCREENSHOT_COUNT = 4
    SILENT = False
    START_TIME = "00:00:00"
    TIME_FORMAT = "%H:%M:%S"