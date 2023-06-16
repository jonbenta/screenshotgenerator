from __future__ import annotations
import itertools
import logging
from typing import Optional
from autogluon.multimodal import MultiModalPredictor
from contextlib import redirect_stderr, redirect_stdout
from gdown import download
from os import devnull
from pandas import DataFrame
from pathlib import Path
from shutil import copy
from tempfile import gettempdir
from zipfile import ZipFile

from .defaults import Defaults
from .portrait_preference import PortraitPreference
from .screenshot import Screenshot

def select(pool_directory: str, screenshot_directory: str, models_directory: Optional[str] = Defaults.MODELS_DIRECTORY, 
           pool_file_filter: Optional[str] = None, portrait_preference: Optional[PortraitPreference] = Defaults.PORTRAIT_PREFERENCE, 
           screenshot_count: Optional[int] = Defaults.SCREENSHOT_COUNT, silent: Optional[bool] = Defaults.SILENT) -> list[Screenshot]:
    
    if Path(models_directory).exists():
        if not Path(models_directory, "focused").is_dir() or not Path(models_directory, "portrait").is_dir():
            raise ValueError(f"'{models_directory}' must contain 'focused' and 'portrait' subdirectories.")
    else:
        _download_models(models_directory, silent)

    if not Path(pool_directory).is_dir():
        raise ValueError(f"'{pool_directory}' is not a directory.")

    Path(screenshot_directory).mkdir(parents=True, exist_ok=True)
    screenshot_paths = [str(f) for f in Path(pool_directory).iterdir() if not pool_file_filter or f.name.startswith(pool_file_filter)]

    if silent:
        with open(devnull, "w") as nowhere, redirect_stdout(nowhere), redirect_stderr(nowhere):
            logging.disable(logging.CRITICAL)
            scored_screenshots = _score_screenshots(screenshot_paths, models_directory)
            logging.disable(logging.NOTSET)
    else:
        scored_screenshots = _score_screenshots(screenshot_paths, models_directory)

    sorted_screenshots = _sort_screenshots(scored_screenshots, portrait_preference)

    for s in sorted_screenshots[:screenshot_count]:
        copy(s.path, Path(screenshot_directory, Path(s.path).name))

    return sorted_screenshots

def _download_models(models_directory: str, silent: bool):
    models_zip_path = Path(gettempdir(), "models.zip")
    download(id="1SqlxSoBnmxdM3cMn3KkLqyR1GBwOiiak", output=str(models_zip_path), quiet=silent)

    if not models_zip_path.exists():
        raise RuntimeError("Failed to download models.")

    with ZipFile(models_zip_path, "r") as models_zip:
        models_zip.extractall(models_directory)

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