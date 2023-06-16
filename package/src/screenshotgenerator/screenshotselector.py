from __future__ import annotations
import click

from .click_enum_type import EnumType
from .common import write_pool_report
from .defaults import Defaults
from .portrait_preference import PortraitPreference
from .screenshot import Screenshot
from .select import select

@click.command()
@click.option("--models-directory",
              type=str,
              default=Defaults.MODELS_DIRECTORY,
              show_default=True,
              help="The path to the directory containing the autogluon models. If the directory doesn't exist, the pretrained models will be downloaded to this location.")
@click.option("--pool-directory",
              type=str,
              required=True,
              help="The directory containing the existing pool of screenshots.")
@click.option("--pool-file-filter",
              type=str,
              default=None,
              show_default=False,
              help='A "starts with" filter for files in the pool directory. Defaults to operating on all files in the pool directory.')
@click.option("--pool-report-path",
              type=str,
              default=None,
              show_default=True,
              help="A JSON file detailing the screenshot pool, sorted by descending preference.")
@click.option("--portrait-preference",
              type=EnumType(PortraitPreference),
              default=Defaults.PORTRAIT_PREFERENCE.value,
              show_default=True,
              help="Preference regarding portrait screenshots.")
@click.option("--screenshot-count",
              type=int,
              default=Defaults.SCREENSHOT_COUNT,
              show_default=True,
              help="The number of screenshots to select.")
@click.option("--screenshot-directory",
              type=str,
              required=True,
              help="The directory into which to copy the selected screenshots.")
@click.option("--silent",
              is_flag=True,
              default=Defaults.SILENT,
              show_default=True,
              help="Suppress autogluon output.")

def main(models_directory: str, pool_directory: str, pool_file_filter: str, pool_report_path: str, portrait_preference: PortraitPreference,
         screenshot_count: int, screenshot_directory: str, silent: bool):
    sorted_screenshots = select(
        models_directory=models_directory,
        pool_directory=pool_directory,
        pool_file_filter=pool_file_filter,
        portrait_preference=portrait_preference,
        screenshot_count=screenshot_count,
        screenshot_directory=screenshot_directory,
        silent=silent)

    write_pool_report(pool_report_path, sorted_screenshots)

if __name__ == "__main__":
    main()