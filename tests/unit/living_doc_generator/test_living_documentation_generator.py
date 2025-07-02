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
from living_doc_utilities.model.issues import Issues

from action_inputs import ActionInputs
from living_doc_generator.living_doc_generator import MdocLivingDocumentationGenerator


# generate


def test_generate_correct_behaviour(mocker):
    # Arrange
    generator: MdocLivingDocumentationGenerator = MdocLivingDocumentationGenerator("/path/to/output")
    mock_clean_output_directory = mocker.patch.object(generator, "_clean_output_directory")
    mock_generate_living_documents = mocker.patch.object(generator, "_generate_living_documents", return_value=True)
    mock_logger_info = mocker.patch("living_doc_generator.living_doc_generator.logger.info")
    mock_logger_debug = mocker.patch("living_doc_generator.living_doc_generator.logger.debug")
    mock_issues_load = mocker.patch("living_doc_utilities.model.issues.Issues.load_from_json")
    mock_issues_load.return_value = Issues()
    mock_action_inputs = mocker.patch("action_inputs.ActionInputs.get_source", return_value="mocked_source")

    # Act
    generator.generate()

    # Assert
    mock_clean_output_directory.assert_called_once()
    mock_generate_living_documents.assert_called_once()
    mock_action_inputs.assert_called_once()
    mock_issues_load.assert_called_once_with(ActionInputs.get_source())
    mock_logger_debug.assert_called_once_with("Output directory cleaned.")
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Loading of issue from source - started."),
            mocker.call("Loading of issue from source - finished."),
            mocker.call("Generating Living Documentation output - started."),
            mocker.call("Generating Living Documentation output - finished."),
        ],
        any_order=True,
    )


# _clean_output_directory


def test_clean_output_directory_correct_behaviour(mocker):
    # Arrange
    generator: MdocLivingDocumentationGenerator = MdocLivingDocumentationGenerator("/path/to/output")
    mock_rmtree = mocker.patch("shutil.rmtree")
    mock_makedirs = mocker.patch("os.makedirs")

    # Act
    generator._clean_output_directory()

    # Assert
    mock_rmtree.assert_called_once()
    mock_makedirs.assert_called_once()


# _generate_living_documents


def test_generate_living_documents_correct_behaviour(mocker, tmp_path, sample_issues_with_project_states, mdoc_exporter):
    # Arrange
    generator: MdocLivingDocumentationGenerator = MdocLivingDocumentationGenerator(str(tmp_path))
    mock_logger_info = mocker.patch("living_doc_generator.living_doc_generator.logger.info")
    mock_logger_error = mocker.patch("living_doc_generator.living_doc_generator.logger.error")
    mocker.patch("living_doc_generator.mdoc_exporter.MdocExporter.export", return_value=True)

    # Act
    res = generator._generate_living_documents(sample_issues_with_project_states)

    # Assert
    assert res
    mock_logger_info.assert_called_once_with("Living Documentation mdoc output generated successfully.")
    mock_logger_error.assert_not_called()


def test_generate_living_documents_fail(mocker, tmp_path, sample_issues_with_project_states, mdoc_exporter):
    # Arrange
    generator: MdocLivingDocumentationGenerator = MdocLivingDocumentationGenerator(str(tmp_path))
    mock_logger_info = mocker.patch("living_doc_generator.living_doc_generator.logger.info")
    mock_logger_error = mocker.patch("living_doc_generator.living_doc_generator.logger.error")
    mocker.patch("living_doc_generator.mdoc_exporter.MdocExporter.export", return_value=False)

    # Act
    res = generator._generate_living_documents(sample_issues_with_project_states)

    # Assert
    assert not res
    mock_logger_info.assert_not_called()
    mock_logger_error.assert_called_once_with("Living Documentation mdoc output generation failed.")
