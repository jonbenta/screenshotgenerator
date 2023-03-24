from __future__ import annotations
import click
import subprocess
from autogluon.multimodal import MultiModalPredictor
from common import get_model_path
from pandas import DataFrame
from pathlib import Path
from pymediainfo import MediaInfo
from shutil import copy
from tempfile import gettempdir

@click.command()
@click.option("--ffmpeg-path", default="ffmpeg", type=str, help="The path to ffmpeg. Defaults to 'ffmpeg', which requires ffmpeg to be in your path.")
@click.option("--pool-directory", default=gettempdir(), type=str, help="The directory in which to store the screenshot pool. Defaults to the temp directory.")
@click.option("--pool-report-path", default=None, type=str, help="A text file listing all pool files in order of descending score. Defaults to not generating the report.")
@click.option("--pool-size", default=64, type=int, help="The size of the pool from which to select screenshots. Defaults to 64.")
@click.option("--screenshot-count", default=4, type=int, help="The number of screenshots to generate. Defaults to 4.")
@click.option("--screenshot-directory", required=True, type=str, help="The directory in which to store the screenshots.")
@click.option("--video-path", required=True, type=str, help="The path to the video for which to generate screenshots.")

def main(ffmpeg_path: str, pool_directory: str, pool_report_path: str, pool_size: int, screenshot_count: int, screenshot_directory: str, video_path: str):
    if pool_size < screenshot_count:
        raise ValueError("--pool-size must be greater than --screenshot_count.")

    Path(pool_directory).mkdir(parents=True, exist_ok=True)
    Path(screenshot_directory).mkdir(parents=True, exist_ok=True)
    screenshot_template = str(Path(pool_directory, f"{Path(video_path).stem}-%d.png"))

    video_track = MediaInfo.parse(video_path).video_tracks[0]
    duration_in_seconds = (float(video_track.duration) / 1000) * 0.95 # Reduce duration by 5% to exclude credits.
    fps = pool_size / duration_in_seconds

    subprocess.call([
        ffmpeg_path,
        "-skip_frame", "nokey",
        "-y",
        "-i", video_path,
        "-frames:v", str(pool_size),
        "-pred", "mixed",
        "-vf", f"fps={fps}",
        screenshot_template
    ])

    screenshots = [str(f) for f in Path(pool_directory).iterdir() if f.name.startswith(Path(video_path).stem)]
    ordered_screenshots = order_by_score_desc(screenshots)
    write_pool_report(pool_report_path, ordered_screenshots)

    for f in ordered_screenshots[:screenshot_count]:
        copy(f, Path(screenshot_directory, Path(f).name))


def order_by_score_desc(screenshots: list) -> list[str]:
    data = DataFrame(screenshots, columns=["file"])
    focused_scores = MultiModalPredictor.load(str(get_model_path("focused"))).predict_proba(data=data).Yes.values
    portrait_scores = MultiModalPredictor.load(str(get_model_path("portrait"))).predict_proba(data=data).Yes.values

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