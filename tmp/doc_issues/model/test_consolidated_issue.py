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

from living_doc_generator.model.consolidated_issue import ConsolidatedIssue


# generate_page_filename


def test_generate_page_filename_inherited_class_attribute_error():
    # Arrange
    class TestConsolidatedIssue(ConsolidatedIssue):
        @property
        def labels(self):
            raise AttributeError("Mocked AttributeError")

    test_issue = TestConsolidatedIssue("test_org/test_repo")

    # Act
    result = test_issue.generate_page_filename()

    # Assert
    assert result == "0.md"
    assert test_issue.errors == {
        "AttributeError": "Issue page filename generation failed (issue does not have a title)."
    }
