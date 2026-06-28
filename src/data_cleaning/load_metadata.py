from pathlib import Path
import pandas as pd


def load_raw_metadata(metadata_path: str | Path) -> pd.DataFrame:
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")
    return pd.read_csv(path)
