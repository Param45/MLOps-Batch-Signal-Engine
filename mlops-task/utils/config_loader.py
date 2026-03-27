import os
from typing import Any, Dict

import yaml

from utils import ConfigValidationError



_SCHEMA: Dict[str, Dict[str, Any]] = {
    "seed": {"type": int, "min": 0},
    "window": {"type": int, "min": 1},
    "version": {"type": str},
}


def load_config(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")


    with open(path, "r", encoding="utf-8") as fh:
        try:
            config = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ConfigValidationError(f"Failed to parse YAML: {exc}") from exc

    if not isinstance(config, dict):
        raise ConfigValidationError(
            f"Config must be a YAML mapping, got {type(config).__name__}"
        )


    missing = [key for key in _SCHEMA if key not in config]
    if missing:
        raise ConfigValidationError(f"Missing required config keys: {missing}")

    for key, rules in _SCHEMA.items():
        value = config[key]
        expected_type = rules["type"]

        if not isinstance(value, expected_type):
            raise ConfigValidationError(
                f"Config key '{key}' must be {expected_type.__name__}, "
                f"got {type(value).__name__} ({value!r})"
            )

        if "min" in rules and value < rules["min"]:
            raise ConfigValidationError(
                f"Config key '{key}' must be >= {rules['min']}, got {value}"
            )

    return config
