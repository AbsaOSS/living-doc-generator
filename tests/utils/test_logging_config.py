#
# Copyright 2024 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
import logging
import os
import sys
from logging import StreamHandler

from living_documentation_generator.utils.logging_config import setup_logging

pytestmark = pytest.mark.setup_logging


def validate_logging_config(mock_logging_setup, caplog, expected_level, expected_message):
    mock_logging_setup.assert_called_once()

    # Get the actual call arguments from the mock
    call_args = mock_logging_setup.call_args[1]  # Extract the kwargs from the call

    # Validate the logging level and format
    assert call_args["level"] == expected_level
    assert call_args["format"] == "%(asctime)s - %(levelname)s - %(message)s"
    assert call_args["datefmt"] == "%Y-%m-%d %H:%M:%S"

    # Check that the handler is a StreamHandler and outputs to sys.stdout
    handlers = call_args["handlers"]
    assert len(handlers) == 1  # Only one handler is expected
    assert isinstance(handlers[0], StreamHandler)  # Handler should be StreamHandler
    assert handlers[0].stream is sys.stdout  # Stream should be sys.stdout

    # Check that the log message is present
    assert expected_message in caplog.text


def test_setup_logging_default_logging_level(mock_logging_setup, caplog):
    with caplog.at_level(logging.INFO):
        setup_logging()

    validate_logging_config(mock_logging_setup, caplog, logging.INFO, "Logging configuration set up.")


def test_setup_logging_verbose_logging_enabled(mock_logging_setup, caplog):
    os.environ["INPUT_VERBOSE_LOGGING"] = "true"

    with caplog.at_level(logging.DEBUG):
        setup_logging()

    validate_logging_config(mock_logging_setup, caplog, logging.DEBUG, "Verbose logging enabled.")


def test_setup_logging_debug_mode_enabled_by_ci(mock_logging_setup, caplog):
    os.environ["RUNNER_DEBUG"] = "1"

    with caplog.at_level(logging.DEBUG):
        setup_logging()

    validate_logging_config(mock_logging_setup, caplog, logging.DEBUG, "Debug mode enabled by CI runner.")
