from pathlib import Path
import pandas as pd

from shared.schemas import CLEAN_MANIFEST_COLUMNS


def load_clean_manifest(manifest_path: str | Path) -> pd.DataFrame:
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")
    return pd.read_csv(path)


def validate_manifest_schema(df: pd.DataFrame) -> list[str]:
    return [column for column in CLEAN_MANIFEST_COLUMNS if column not in df.columns]


def select_valid_records(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["record_status"] == "valid"].copy()
