from __future__ import annotations
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from pymediainfo import MediaInfo
from shutil import which

from .defaults import Defaults
from .portrait_preference import PortraitPreference
from .screenshot import Screenshot
from .select import select

def generate(screenshot_directory: str, video_path: str, end_time: Optional[datetime] = Defaults.END_TIME, ffmpeg_path: Optional[str] = Defaults.FFMPEG_PATH, 
             models_directory: Optional[str] = Defaults.MODELS_DIRECTORY, pool_directory: Optional[str] = Defaults.POOL_DIRECTORY, 
             pool_size: Optional[int] = Defaults.POOL_SIZE, portrait_preference: Optional[PortraitPreference] = Defaults.PORTRAIT_PREFERENCE,
             screenshot_count: Optional[int] = Defaults.SCREENSHOT_COUNT, silent: Optional[bool] = Defaults.SILENT, 
             start_time: Optional[datetime] = datetime.strptime(Defaults.START_TIME, Defaults.TIME_FORMAT)) -> list[Screenshot]:
    
    if not Path(video_path).is_file():
        raise ValueError(f"'{video_path}' is not a file.")
    if which(ffmpeg_path) is None:
        raise ValueError(f"'{ffmpeg_path}' does not exist.")

    video_duration_in_seconds = float(MediaInfo.parse(video_path).video_tracks[0].duration) / 1000
    end_time_in_seconds = _datetime_to_seconds(end_time) if end_time else video_duration_in_seconds * 0.95
    start_time_in_seconds = _datetime_to_seconds(start_time)

    if start_time_in_seconds >= video_duration_in_seconds:
        raise ValueError("Start time must be less than video duration.")
    if end_time_in_seconds >= video_duration_in_seconds:
        raise ValueError("End time must be less than video duration.")
    if start_time_in_seconds >= end_time_in_seconds:
        raise ValueError("Start time must be less than end time.")

    Path(pool_directory).mkdir(parents=True, exist_ok=True)
    screenshot_template = str(Path(pool_directory, f"{Path(video_path).stem}-%d.png"))

    screenshot_duration_in_seconds = end_time_in_seconds - start_time_in_seconds
    fps = pool_size / screenshot_duration_in_seconds

    subprocess_output = subprocess.DEVNULL if silent else None
    subprocess.call([
        ffmpeg_path,
        "-skip_frame", "nokey",
        "-y",
        "-i", video_path,
        "-ss", start_time.strftime(Defaults.TIME_FORMAT),
        "-frames:v", str(pool_size),
        "-pred", "mixed",
        "-vf", f"fps={fps}",
        screenshot_template
    ], stdout=subprocess_output, stderr=subprocess_output)

    return select(
        pool_directory=pool_directory, 
        screenshot_directory=screenshot_directory, 
        models_directory=models_directory, 
        pool_file_filter=Path(video_path).stem, 
        portrait_preference=portrait_preference, 
        screenshot_count=screenshot_count, 
        silent=silent)

def _datetime_to_seconds(time: datetime) -> int:
    return timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds()