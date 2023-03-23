from pathlib import Path

def get_model_path(model_name: str) -> Path:
    return Path(Path(__file__).parent, "models", model_name)