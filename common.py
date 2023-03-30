from pathlib import Path

def get_model_path(model_name: str) -> Path:
    return Path(get_models_directory(), model_name)

def get_models_directory() -> Path:
    return Path(Path(__file__).parent, "models")