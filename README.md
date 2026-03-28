# MLOps Batch Pipeline

A production-quality, Dockerized MLOps batch pipeline that processes BTC trading data to generate rolling-mean-based trading signals. Demonstrates **reproducibility**, **observability**, and **deployment readiness**.

---

## Architecture

```
project-root/
│
├── data.csv                # Input dataset (BTC 1-min OHLCV candles)
│
└── mlops-task/
    ├── run.py              # CLI entry point — orchestrates the pipeline
    ├── config.yaml         # Pipeline configuration (seed, window, version, paths)
    ├── requirements.txt    # Python dependencies
    ├── Dockerfile          # Containerized deployment setup
    ├── README.md           # Project documentation
    ├── metrics.json        # Output — structured pipeline metrics
    ├── run.log             # Output — structured pipeline logs
    │
    └── utils/
        ├── __init__.py         # Package init + custom exceptions
        ├── config_loader.py    # YAML config loading & path resolution
        ├── data_loader.py      # CSV ingestion & validation
        ├── processor.py        # Rolling mean, signal generation, metrics
        └── logger.py           # Structured logging setup
```

## Features

| Feature | Description |
|---------|-------------|
| **Modular Design** | Clean separation of concerns across `utils/` modules |
| **Schema Validation** | Config keys validated for type, presence, and range |
| **Deterministic Runs** | Seed enforced via `numpy.random.seed()` — identical outputs guaranteed |
| **Structured Logging** | Timestamped, leveled logs to file + stdout |
| **Graceful Error Handling** | Custom exceptions; error metrics always written on failure |
| **Timing Decorator** | Latency measurement via `@timing` decorator |
| **CLI Validation** | `argparse` with required arguments |
| **Docker Ready** | Single `docker run` to execute the full pipeline |

---

## Local Run

```bash
pip install -r requirements.txt
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Docker

```bash
docker build -t mlops-task .
docker run --rm mlops-task
```

---

## Sample Output

### metrics.json (Success)

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}
```

### metrics.json (Error)

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Missing required columns: ['close']. Found columns: [...]"
}
```

---

## Determinism Verification

Run the pipeline twice and compare outputs:

```bash
python run.py --input data.csv --config config.yaml --output metrics1.json --log-file run1.log
python run.py --input data.csv --config config.yaml --output metrics2.json --log-file run2.log
diff metrics1.json metrics2.json  # Should show no differences (except latency_ms)
```

The `signal_rate`, `rows_processed`, and all non-timing fields will be **identical** across runs.
