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
from github.Issue import Issue

from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue


# generate_page_filename


def test_generate_page_filename_correct_behaviour():
    # Arrange
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = consolidated_issue.generate_page_filename()

    # Assert
    assert "1_issue_title.md" == actual


def test_generate_page_filename_with_none_title(mocker):
    # Arrange
    mock_issue = Issue(None, None, {"number": 1, "title": None}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_page_filename()

    # Assert
    assert "1.md" == actual
    assert mock_consolidated_issue.errors == {
        "AttributeError": "Issue page filename generation failed (issue does not have a title)."
    }


# generate_directory_path


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_disabled(mocker):
    # Arrange
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.make_absolute_path",
        return_value="/mocked/absolute/output/path/",
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_directory_path("issue table")

    # Assert
    assert ["/mocked/absolute/output/path/"] == actual


def test_generate_directory_path_structured_output_enabled_grouping_by_topics_disabled(mocker):
    # Arrange
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.make_absolute_path",
        return_value="/mocked/absolute/output/path/",
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_directory_path("issue table")

    # Assert
    assert ["/mocked/absolute/output/path/organization/repository"] == actual


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_enabled_two_issue_topics(mocker):
    # Arrange
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.make_absolute_path",
        return_value="/mocked/absolute/output/path/",
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.ConsolidatedIssue.validate_labels", return_value=None
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_directory_path("| Labels | feature, BETopic, FETopic |")

    # Assert
    assert ["/mocked/absolute/output/path/BETopic", "/mocked/absolute/output/path/FETopic"] == actual


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_enabled_no_issue_topics(mocker):
    # Arrange
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.make_absolute_path",
        return_value="/mocked/absolute/output/path/",
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.ConsolidatedIssue.validate_labels",
        return_value=["/mocked/absolute/output/path/NoTopic"],
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_directory_path("| Labels | feature, bug |")

    # Assert
    assert ["/mocked/absolute/output/path/NoTopic"] == actual


def test_generate_directory_path_structured_output_enabled_grouping_by_topics_enabled_one_issue_topic(mocker):
    # Arrange
    mock_log_debug = mocker.patch("living_documentation_regime.model.consolidated_issue.logger.debug")
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.make_absolute_path",
        return_value="/mocked/absolute/output/path/",
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_regime.model.consolidated_issue.ConsolidatedIssue.validate_labels", return_value=None
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.generate_directory_path(
        "| Labels | DocumentedFeature, DocumentedUS, BETopic, FETopic |"
    )

    # Assert
    assert [
        "/mocked/absolute/output/path/organization/repository/BETopic",
        "/mocked/absolute/output/path/organization/repository/FETopic",
    ] == actual


# validate_labels


def test_validate_labels_no_topic_labels(mocker):
    # Arrange
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.validate_labels(["DocumentedFeature"], [], "/mocked/absolute/output/path/")

    # Assert
    assert ["/mocked/absolute/output/path/NoTopic"] == actual
    assert mock_consolidated_issue.topics == ["NoTopic"]
    assert mock_consolidated_issue.errors == {"TopicError": "No Topic label found."}


def test_validate_labels_multiple_topics_and_multiple_documented_labels(mocker):
    # Arrange
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.validate_labels(
        ["DocumentedFeature", "DocumentedUS"], ["BETopic", "FETopic"], "/mocked/absolute/output/path/"
    )

    # Assert
    assert not actual
    assert mock_consolidated_issue.errors == {
        "DocumentationError": "More than one Documentation label found.",
        "TopicError": "More than one Topic label found.",
    }


def test_validate_labels_topic_label_without_documented_label(mocker):
    # Arrange
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    mock_consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    # Act
    actual = mock_consolidated_issue.validate_labels([], ["BETopic"], "/mocked/absolute/output/path/")

    # Assert
    assert not actual
    assert mock_consolidated_issue.errors == {"DocumentationError": "Topic label found without Documentation one."}
