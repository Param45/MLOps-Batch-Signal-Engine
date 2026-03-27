

import argparse
import json
import sys
import time

import numpy as np

from utils import (
    ConfigValidationError,
    DataValidationError,
    PipelineError,
    compute_metrics,
    compute_rolling_mean,
    generate_signal,
    load_config,
    load_data,
    setup_logger,
)



def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MLOps Batch Pipeline — rolling-mean signal generator",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV data file.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output metrics JSON file.",
    )
    parser.add_argument(
        "--log-file",
        required=True,
        help="Path for the pipeline log file.",
    )
    return parser.parse_args()



def _save_metrics(metrics: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)


def _error_metrics(version: str, message: str) -> dict:
    return {
        "version": version,
        "status": "error",
        "error_message": str(message),
    }



def main() -> None:
    args = _parse_args()

    
    version = "unknown"

    
    logger = setup_logger(args.log_file)

    try:

        start_time = time.perf_counter()

        logger.info("=" * 60)
        logger.info("Pipeline started")
        logger.info("=" * 60)


        logger.info("Loading config from: %s", args.config)
        config = load_config(args.config)
        version = config["version"]
        seed = config["seed"]
        window = config["window"]
        logger.info(
            "Config loaded — version=%s, seed=%d, window=%d",
            version, seed, window,
        )


        np.random.seed(seed)
        logger.info("Random seed set to %d", seed)


        logger.info("Loading data from: %s", args.input)
        df = load_data(args.input)
        logger.info("Data loaded — %d rows, %d columns", len(df), len(df.columns))


        logger.info("Computing rolling mean (window=%d)", window)
        if window >= len(df):
            logger.warning(
                "Window (%d) is >= dataset size (%d). Almost all signals will be NaN.",
                window, len(df)
            )
        df = compute_rolling_mean(df, window)
        logger.info("Rolling mean computed")


        logger.info("Generating trading signals")
        df = generate_signal(df)
        signal_count = int(df["signal"].dropna().sum())
        total_valid = int(df["signal"].dropna().count())
        logger.info(
            "Signals generated — %d/%d rows signalled BUY",
            signal_count, total_valid,
        )


        logger.info("Computing metrics")
        metrics = compute_metrics(df, start_time, version, seed)

        
        metrics.pop("_elapsed_ms", None)

        _save_metrics(metrics, args.output)
        logger.info("Metrics saved to: %s", args.output)


        print(json.dumps(metrics, indent=2))

        logger.info("=" * 60)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 60)

    except (
        FileNotFoundError,
        ConfigValidationError,
        DataValidationError,
        PipelineError,
    ) as exc:
        logger.error("Pipeline failed: %s", exc)
        _save_metrics(_error_metrics(version, str(exc)), args.output)
        sys.exit(1)

    except Exception as exc:  
        logger.error("Unexpected error: %s", exc, exc_info=True)
        _save_metrics(_error_metrics(version, str(exc)), args.output)
        sys.exit(1)


if __name__ == "__main__":
    main()
