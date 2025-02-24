# Copyright 2025 ABSA Group Limited
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

"""
This module contains a factory class for creating exporters.
"""
import logging
from living_documentation_regime.exporter.mdoc_exporter import MdocExporter
from utils.constants import Regime, Format

logger = logging.getLogger(__name__)


class ExporterFactory:
    """
    A factory class for creating exporters based on adequate regime and format.
    """

    @staticmethod
    def get_exporter(regime: Regime, fmt: str):
        match (regime, fmt):
            case (Regime.LIV_DOC_REGIME, Format.MDOC.value):
                return MdocExporter()
            case _:
                logger.error("Exporter not found for regime: %s and format: %s", regime, fmt)
                return None
