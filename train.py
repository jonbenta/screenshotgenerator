from __future__ import annotations
import click
from autogluon.multimodal import MultiModalPredictor
from common import get_model_path
from pandas import DataFrame
from pathlib import Path
from shutil import rmtree

@click.command()
@click.option("--focused-directory", required=True, type=str, help="The directory containing training images for the focused model, organized into 'Yes' and 'No' subdirectories.")
@click.option("--portrait-directory", required=True, type=str, help="The directory containing training images for the portrait model, organized into 'Yes' and 'No' subdirectories.")
@click.option("--training-time-limit", default=None, type=int, help="The training time limit (seconds). Defaults to letting autogluon run until it's had enough.")

def main(focused_directory: str, portrait_directory: str, training_time_limit: int):
    train(focused_directory, "focused", training_time_limit)
    train(portrait_directory, "portrait", training_time_limit)


def train(directory: str, model_name: str, time_limit: int):
    model_path = get_model_path(model_name)
    training_data = []

    if model_path.exists():
        if click.confirm(f"A {model_name} model already exists. Do you wish to overwrite it?", default=False):
            rmtree(model_path)
        else:
            return
        
    subdirectories = [d for d in Path(directory).iterdir() if d.is_dir()]
    subdirectory_names = [d.name for d in subdirectories]

    if len(subdirectory_names) != 2 or 'Yes' not in subdirectory_names or 'No' not in subdirectory_names:
        raise ValueError(f"'{directory}' must contain exactly 2 subdirectories, named 'Yes' and 'No'.")
    
    for subdirectory in subdirectories:
        label = subdirectory.name

        for file in Path(subdirectory).iterdir():
            training_data.append([str(file), label])
            
    training_data_frame = DataFrame(training_data, columns=["file", "label"])

    predictor = MultiModalPredictor(label="label", path=str(model_path), problem_type="binary")
    predictor.fit(train_data=training_data_frame, time_limit=time_limit)

if __name__ == "__main__":
    main()