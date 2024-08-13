import logging
import os


def setup_logging() -> None:
    is_verbose_logging: bool = (
        os.getenv("INPUT_VERBOSE_LOGGING", "false").lower() == "true"
    )
    is_debug_mode = os.getenv("RUNNER_DEBUG", "0") == "1"
    level = logging.DEBUG if is_verbose_logging or is_debug_mode else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
