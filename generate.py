from __future__ import annotations
import click
import subprocess
from autogluon.multimodal import MultiModalPredictor
from common import get_model_path
from datetime import datetime, timedelta
from pandas import DataFrame
from pathlib import Path
from pymediainfo import MediaInfo
from shutil import copy
from tempfile import gettempdir

@click.command()
@click.option("--end-time", default=None, type=click.DateTime(formats=["%H:%M:%S"]), help="The time at which to stop taking screenshots. Defaults to 95% of the video duration, to exclude credits.")
@click.option("--ffmpeg-path", default="ffmpeg", type=str, help="The path to ffmpeg. Defaults to 'ffmpeg', which requires ffmpeg to be in your path.")
@click.option("--pool-directory", default=gettempdir(), type=str, help="The directory in which to store the screenshot pool. Defaults to the temp directory.")
@click.option("--pool-report-path", default=None, type=str, help="A text file listing all pool files in order of descending score. Defaults to not generating the report.")
@click.option("--pool-size", default=64, type=int, help="The size of the pool from which to select screenshots. Defaults to 64.")
@click.option("--portrait-preference", default="portrait", type=click.Choice(["portrait", "mixed", "noportrait"]), help="Preference regarding portrait screenshots. Defaults to 'portrait'.")
@click.option("--screenshot-count", default=4, type=int, help="The number of screenshots to generate. Defaults to 4.")
@click.option("--screenshot-directory", required=True, type=str, help="The directory in which to store the screenshots.")
@click.option("--start-time", default="00:00:00", type=click.DateTime(formats=["%H:%M:%S"]), help="The time at which to start taking screenshots. Defaults to 00:00:00.")
@click.option("--video-path", required=True, type=str, help="The path to the video for which to generate screenshots.")

def main(end_time: datetime, ffmpeg_path: str, pool_directory: str, pool_report_path: str, pool_size: int, portrait_preference: str, screenshot_count: int, screenshot_directory: str, start_time: datetime, video_path: str):
    if pool_size < screenshot_count:
        raise ValueError("--pool-size must be greater than --screenshot_count.")

    Path(pool_directory).mkdir(parents=True, exist_ok=True)
    Path(screenshot_directory).mkdir(parents=True, exist_ok=True)
    screenshot_template = str(Path(pool_directory, f"{Path(video_path).stem}-%d.png"))

    video_duration_in_seconds = float(MediaInfo.parse(video_path).video_tracks[0].duration) / 1000
    end_time_in_seconds = time_in_seconds(end_time) if end_time else video_duration_in_seconds * 0.95
    screenshot_duration_in_seconds = end_time_in_seconds - time_in_seconds(start_time)
    fps = pool_size / screenshot_duration_in_seconds

    subprocess.call([
        ffmpeg_path,
        "-skip_frame", "nokey",
        "-y",
        "-i", video_path,
        "-ss", start_time.strftime("%H:%M:%S"),
        "-frames:v", str(pool_size),
        "-pred", "mixed",
        "-vf", f"fps={fps}",
        screenshot_template
    ])

    screenshots = [str(f) for f in Path(pool_directory).iterdir() if f.name.startswith(Path(video_path).stem)]
    ordered_screenshots = order_by_score_desc(screenshots, portrait_preference)
    write_pool_report(pool_report_path, ordered_screenshots)

    for f in ordered_screenshots[:screenshot_count]:
        copy(f, Path(screenshot_directory, Path(f).name))

def time_in_seconds(time: datetime) -> int:
    return timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds()

def order_by_score_desc(screenshots: list, portrait_preference: str) -> list[str]:
    data = DataFrame(screenshots, columns=["file"])
    focused_scores = MultiModalPredictor.load(str(get_model_path("focused"))).predict_proba(data=data).Yes.values

    if portrait_preference == "portrait":
        portrait_scores = MultiModalPredictor.load(str(get_model_path("portrait"))).predict_proba(data=data).Yes.values
    elif portrait_preference == "noportrait":
        portrait_scores = MultiModalPredictor.load(str(get_model_path("portrait"))).predict_proba(data=data).No.values
    else:
        portrait_scores = [0] * len(screenshots)

    scored_screenshots = [{
        "path": path, 
        "focused_score": focused_scores[index],
        "portrait_score": portrait_scores[index]
    } for index, path in enumerate(screenshots)]

    scored_screenshots = sorted(scored_screenshots, key=lambda s: (s['focused_score'] * 0.75) + (s['portrait_score'] * 0.25), reverse=True)
    return [ss['path'] for ss in scored_screenshots]

def write_pool_report(report_path: str, ordered_screenshots: list):
    if not report_path:
        return
    
    pool_list_file = open(report_path, "w")
    pool_list_file.writelines(ordered_screenshots)
    pool_list_file.close()

if __name__ == "__main__":
    main()