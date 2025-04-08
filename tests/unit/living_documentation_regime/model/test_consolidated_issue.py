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




# generate_directory_path




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
