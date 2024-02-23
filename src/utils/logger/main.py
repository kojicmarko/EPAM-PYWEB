import json
import logging.config
import logging.handlers
import pathlib

logger = logging.getLogger("pyweb")


def setup_logging() -> None:
    config_file = pathlib.Path("src/utils/logger/config.json")
    with open(config_file) as f:
        config = json.load(f)

    logging.config.dictConfig(config)
