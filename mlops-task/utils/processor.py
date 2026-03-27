
import functools
import time
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd




def timing(func: Callable) -> Callable:

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        if isinstance(result, dict):
            result["_elapsed_ms"] = elapsed_ms
        else:
            try:
                result._elapsed_ms = elapsed_ms  
            except AttributeError:
                pass
        return result

    return wrapper




def compute_rolling_mean(df: pd.DataFrame, window: int) -> pd.DataFrame:
    df = df.copy()
    df["rolling_mean"] = df["close"].rolling(window=window).mean()
    return df


def generate_signal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["signal"] = np.where(
        df["rolling_mean"].isna(),
        np.nan,
        np.where(df["close"] > df["rolling_mean"], 1, 0),
    )
    return df


@timing
def compute_metrics(
    df: pd.DataFrame,
    start_time: float,
    version: str,
    seed: int,
) -> Dict[str, Any]:
    valid_signals = df["signal"].dropna()
    signal_rate = round(float(valid_signals.mean()), 4)
    latency_ms = round((time.perf_counter() - start_time) * 1000)

    return {
        "version": version,
        "rows_processed": len(df),
        "metric": "signal_rate",
        "value": signal_rate,
        "latency_ms": latency_ms,
        "seed": seed,
        "status": "success",
    }
