from __future__ import annotations
import itertools
import logging
from re import I
import subprocess
from autogluon.multimodal import MultiModalPredictor
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
from os import devnull
from pandas import DataFrame
from pathlib import Path
from pymediainfo import MediaInfo
from shutil import copy

from .defaults import Defaults
from .portrait_preference import PortraitPreference
from .screenshot import Screenshot

def generate(models_directory: str, screenshot_directory: str, video_path: str, end_time: Optional[datetime] = Defaults.END_TIME, 
             ffmpeg_path: Optional[str] = Defaults.FFMPEG_PATH, pool_directory: Optional[str] = Defaults.POOL_DIRECTORY, 
             pool_size: Optional[int] = Defaults.POOL_SIZE, portrait_preference: Optional[PortraitPreference] = Defaults.PORTRAIT_PREFERENCE,
             screenshot_count: Optional[int] = Defaults.SCREENSHOT_COUNT, silent: Optional[bool] = Defaults.SILENT, 
             start_time: Optional[datetime] = datetime.strptime(Defaults.START_TIME, Defaults.TIME_FORMAT)) -> list[Screenshot]:
    if pool_size <= screenshot_count:
        raise ValueError("Pool size must be greater or equal to screenshot count.")

    Path(pool_directory).mkdir(parents=True, exist_ok=True)
    Path(screenshot_directory).mkdir(parents=True, exist_ok=True)
    screenshot_template = str(Path(pool_directory, f"{Path(video_path).stem}-%d.png"))

    video_duration_in_seconds = float(MediaInfo.parse(video_path).video_tracks[0].duration) / 1000
    end_time_in_seconds = _datetime_to_seconds(end_time) if end_time else video_duration_in_seconds * 0.95
    screenshot_duration_in_seconds = end_time_in_seconds - _datetime_to_seconds(start_time)
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

    screenshot_paths = [str(f) for f in Path(pool_directory).iterdir() if f.name.startswith(Path(video_path).stem)]

    if silent:
        with open(devnull, "w") as nowhere, redirect_stdout(nowhere), redirect_stderr(nowhere):
            logging.disable(logging.CRITICAL)
            scored_screenshots = _score_screenshots(screenshot_paths, models_directory)
            logging.disable(logging.NOTSET)
    else:
        scored_screenshots = _score_screenshots(screenshot_paths, models_directory)

    sorted_screenshots = _sort_screenshots(scored_screenshots, portrait_preference)

    if screenshot_directory:
        for s in sorted_screenshots[:screenshot_count]:
            copy(s.path, Path(screenshot_directory, Path(s.path).name))

    return sorted_screenshots

def _datetime_to_seconds(time: datetime) -> int:
    return timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds()

def _score_screenshots(screenshot_paths: list[str], models_directory: str) -> list[Screenshot]:
    data = DataFrame(screenshot_paths, columns=["file"])
    focused_scores = MultiModalPredictor.load(str(Path(models_directory, "focused"))).predict_proba(data=data).Yes.values
    portrait_scores = MultiModalPredictor.load(str(Path(models_directory, "portrait"))).predict_proba(data=data).Yes.values
    return [Screenshot(path, float(focused_scores[index]), float(portrait_scores[index])) for index, path in enumerate(screenshot_paths)]

def _sort_screenshots(scored_screenshots: list[Screenshot], portrait_preference: PortraitPreference) -> list[Screenshot]:
    screenshots_sorted_by_portrait = sorted(scored_screenshots, key=lambda s: (s.focused_score * 0.75) + (s.portrait_score * 0.25), reverse=True)
    screenshots_sorted_by_noportrait = sorted(scored_screenshots, key=lambda s: (s.focused_score * 0.75) + ((1 - s.portrait_score) * 0.25), reverse=True)

    if portrait_preference == PortraitPreference.PORTRAIT:
        return screenshots_sorted_by_portrait
    elif portrait_preference == PortraitPreference.NO_PORTRAIT:
        return screenshots_sorted_by_noportrait
    elif portrait_preference == PortraitPreference.MIXED:
        screenshots_sorted_by_mixed = itertools.chain(*zip(screenshots_sorted_by_portrait, screenshots_sorted_by_noportrait))
        unique_paths = set()
        return [s for s in screenshots_sorted_by_mixed if not (s.path in unique_paths or unique_paths.add(s.path))]
    else:
        raise ValueError(f"'{portrait_preference}'' is not a valid portrait preference.")