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

from factory.exporter_factory import ExporterFactory
from living_documentation_regime.exporter.mdoc_exporter import MdocExporter
from utils.constants import Regime, Format

def test_get_exporter_liv_doc_regime_mdoc():
    exporter = ExporterFactory.get_exporter(Regime.LIV_DOC_REGIME, Format.MDOC.value, "./output/liv-doc-regime")
    assert isinstance(exporter, MdocExporter)

def test_get_exporter_invalid_regime():
    exporter = ExporterFactory.get_exporter("INVALID_REGIME", Format.MDOC.value, "./output/liv-doc-regime")
    assert exporter is None

def test_get_exporter_invalid_format():
    exporter = ExporterFactory.get_exporter(Regime.LIV_DOC_REGIME, "INVALID_FORMAT", "./output/liv-doc-regime")
    assert exporter is None

def test_get_exporter_invalid_regime_and_format():
    exporter = ExporterFactory.get_exporter("INVALID_REGIME", "INVALID_FORMAT", "./output/liv-doc-regime")
    assert exporter is None
