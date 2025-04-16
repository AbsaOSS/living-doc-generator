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
from typing import Optional
from exporter.exporter import Exporter
from living_documentation_regime.exporter.mdoc_exporter import MdocExporter
from living_documentation_regime.exporter.pdf_exporter import PDFExporter
from utils.constants import Regime, Format

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class ExporterFactory:
    """
    A factory class for creating exporters based on adequate regime and format.
    """

    @staticmethod
    def get_exporter(regime: Regime, fmt: str, regime_output_path: str) -> Optional[Exporter]:
        """
        Get the exporter based on the regime and format.

        @param regime: The regime for which the exporter is needed.
        @param fmt: The format in which the output should be exported.
        @return: The exporter for the regime and format.
        """
        match (regime, fmt):
            case (Regime.LIV_DOC_REGIME, Format.MDOC.value):
                return MdocExporter(regime_output_path)
            case (Regime.LIV_DOC_REGIME, Format.PDF.value):
                return PDFExporter(regime_output_path)
            case _:
                logger.error("Exporter not found for regime: %s and format: %s", regime, fmt)
                return None
