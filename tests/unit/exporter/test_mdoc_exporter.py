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

import pytest

from living_documentation_regime.exporter.mdoc_exporter import MdocExporter
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from utils.constants import REPORT_PAGE_HEADER


@pytest.fixture
def mdoc_exporter():
    return MdocExporter()


# __init__


def test_mdoc_exporter_initialization(mdoc_exporter):
    # Assert
    assert mdoc_exporter._issue_page_detail_template is None
    assert mdoc_exporter._index_page_template is None
    assert mdoc_exporter._index_root_level_page is None
    assert mdoc_exporter._index_org_level_template is None
    assert mdoc_exporter._index_repo_page_template is None
    assert mdoc_exporter._index_data_level_template is None
    assert mdoc_exporter._report_page_template is None
    assert mdoc_exporter._report_page_content == REPORT_PAGE_HEADER


# _export


def test_export_success(mocker, mdoc_exporter):
    # Arrange
    mocker.patch.object(mdoc_exporter, '_load_all_templates', return_value=True)
    mocker.patch.object(mdoc_exporter, '_generate_page_per_issue', return_value=set())
    mocker.patch.object(mdoc_exporter, '_generate_output_structure')
    mocker.patch.object(mdoc_exporter, '_generate_report_page')
    mock_logger_info = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.info')

    issues = {"test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue)}

    # Act
    result = mdoc_exporter.export(issues=issues)

    # Assert
    assert result is True
    mock_logger_info.assert_called_with("MDoc page generation - finished.")


def test_export_failed(mocker, mdoc_exporter):
    # Arrange
    mocker.patch.object(mdoc_exporter, '_load_all_templates', return_value=False)
    mock_logger_info = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.info')

    issues = {"test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue)}

    # Act
    result = mdoc_exporter.export(issues=issues)

    # Assert
    assert result is False
    mock_logger_info.assert_called_with("MDoc page generation - started.")


# _generate_report_page


def test_generate_report_page_no_error(mocker, mdoc_exporter):
    # Arrange
    mock_logger_warning = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.warning')
    mdoc_exporter._report_page_content = "Header\n---"

    # Act
    mdoc_exporter._generate_report_page()

    # Assert
    mock_logger_warning.assert_not_called()


def test_generate_report_page_with_errors(mocker, mdoc_exporter):
    # Arrange
    mocker.patch('living_documentation_regime.exporter.mdoc_exporter.make_absolute_path', return_value='/path')
    mock_open = mocker.patch('builtins.open', mocker.mock_open())
    mock_logger_warning = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.warning')

    mdoc_exporter._report_page_content = "Header\n---\nError"
    mdoc_exporter._report_page_template = "{date} {livdoc_report_page_content}"

    # Act
    mdoc_exporter._generate_report_page()

    # Assert
    mock_open.assert_called_once_with('/path/report_page.md', 'w', encoding='utf-8')
    mock_logger_warning.assert_called_once_with("MDoc page generation - Report page generated.")


# _generate_page_per_issue


def test_generate_page_per_issue(mocker, mdoc_exporter):
    # Arrange
    mock_logger_info = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.info')
    mock_generate_md_issue_page = mocker.patch.object(mdoc_exporter, '_generate_md_issue_page')
    mocker.patch('living_documentation_regime.exporter.mdoc_exporter.ActionInputs.get_is_report_page_generation_enabled', return_value=True)
    issues = {"test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue, topics=["topic1"], errors={"error": "message"}, number=1, repository_id="xxx/yyy", html_url="some/url")}

    mdoc_exporter._report_page_content = ""
    expected = "| error | [xxx/yyy#1](some/url) | message |\n"

    # Act
    topics = mdoc_exporter._generate_page_per_issue(issues)

    # Assert
    assert topics == {"topic1"}
    mock_generate_md_issue_page.assert_called_once()
    assert expected == mdoc_exporter._report_page_content
    mock_logger_info.assert_has_calls(
        [
            mocker.call("MDoc page generation - generated `%i` issue pages.", 1),
            mocker.call("Identified `%i` unique topics.", 1),
        ],
        any_order=False,
    )


# _generate_output_structure


# _generate_md_issue_page


# _generate_structured_index_pages


# _generate_index_page


# _generate_sub_level_index_page


# _generate_mdoc_line


# _generate_issue_summary_table


# _generate_index_directory_path


# _load_all_templates



# def test_generate_output_structure(mocker, mdoc_exporter):
#     mock_generate_root_level_index_page = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.generate_root_level_index_page')
#     mock_generate_structured_index_pages = mocker.patch.object(mdoc_exporter, '_generate_structured_index_pages')
#     mock_generate_index_page = mocker.patch.object(mdoc_exporter, '_generate_index_page')
#     mock_action_inputs = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.ActionInputs.get_is_structured_output_enabled', return_value=True)
#
#     issues = {"test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue)}
#     topics = {"topic1"}
#
#     mdoc_exporter._generate_output_structure(issues, topics)
#
#     mock_generate_root_level_index_page.assert_called_once()
#     mock_generate_structured_index_pages.assert_called_once()
#
# def test_generate_md_issue_page(mocker, mdoc_exporter):
#     mock_generate_issue_summary_table = mocker.patch.object(mdoc_exporter, '_generate_issue_summary_table', return_value="summary_table")
#     mock_generate_directory_path = mocker.patch.object(mocker.Mock(spec=ConsolidatedIssue), 'generate_directory_path', return_value=["/path"])
#     mock_generate_page_filename = mocker.patch.object(mocker.Mock(spec=ConsolidatedIssue), 'generate_page_filename', return_value="filename.md")
#     mock_open = mocker.patch('builtins.open', mocker.mock_open())
#     mock_logger_debug = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.debug')
#
#     consolidated_issue = mocker.Mock(spec=ConsolidatedIssue, title="title", body="body")
#     mdoc_exporter._issue_page_detail_template = "{title} {issue_summary_table} {issue_content}"
#
#     mdoc_exporter._generate_md_issue_page(mdoc_exporter._issue_page_detail_template, consolidated_issue)
#
#     mock_open.assert_called_once_with('/path/filename.md', 'w', encoding='utf-8')
#     mock_logger_debug.assert_called_once_with("Generated MDoc page: filename.md.")
#
# def test_generate_index_directory_path(mocker, mdoc_exporter):
#     mock_make_absolute_path = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.make_absolute_path', return_value='/base_path')
#     mock_os_path_join = mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
#     mock_os_makedirs = mocker.patch('os.makedirs')
#
#     repository_id = "org/repo"
#     topic = "topic1"
#     result = mdoc_exporter._generate_index_directory_path(repository_id, topic)
#
#     assert result == '/base_path/org/repo/topic1'
#     mock_make_absolute_path.assert_called_once_with(LIV_DOC_OUTPUT_PATH)
#     mock_os_path_join.assert_any_call('/base_path', 'org', 'repo')
#     mock_os_path_join.assert_any_call('/base_path/org/repo', 'topic1')
#     mock_os_makedirs.assert_called_once_with('/base_path/org/repo/topic1', exist_ok=True)
#
# def test_load_all_templates(mocker, mdoc_exporter):
#     mock_load_template = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.load_template', return_value="template_content")
#     mock_logger_error = mocker.patch('living_documentation_regime.exporter.mdoc_exporter.logger.error')
#
#     result = mdoc_exporter._load_all_templates()
#
#     assert result is True
#     assert mdoc_exporter._issue_page_detail_template == "template_content"
#     assert mdoc_exporter._index_page_template == "template_content"
#     assert mdoc_exporter._index_root_level_page == "template_content"
#     assert mdoc_exporter._index_org_level_template == "template_content"
#     assert mdoc_exporter._index_repo_page_template == "template_content"
#     assert mdoc_exporter._index_data_level_template == "template_content"
#     assert mdoc_exporter._report_page_template == "template_content"
#     mock_logger_error.assert_not_called()
