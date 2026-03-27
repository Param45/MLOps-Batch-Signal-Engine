import os
from io import StringIO

import pandas as pd

from utils import DataValidationError


_REQUIRED_COLUMNS = {"close"}


def _try_fix_quoted_csv(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()


    cleaned_lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith('"') and stripped.endswith('"'):
            stripped = stripped[1:-1]
        cleaned_lines.append(stripped)

    cleaned_csv = "\n".join(cleaned_lines)
    return pd.read_csv(StringIO(cleaned_csv))


def load_data(path: str) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Data file not found: {path}")


    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise DataValidationError(f"Data file is empty or has no columns: {path}")


    if len(df.columns) == 1 and _REQUIRED_COLUMNS - set(df.columns):
        df = _try_fix_quoted_csv(path)


    if df.empty:
        raise DataValidationError(f"Data file is empty: {path}")


    actual_cols = set(df.columns)
    missing = _REQUIRED_COLUMNS - actual_cols
    if missing:
        raise DataValidationError(
            f"Missing required columns: {sorted(missing)}. "
            f"Found columns: {sorted(actual_cols)}"
        )

    return df
