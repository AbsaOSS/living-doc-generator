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
import os
import pytest

from living_doc_generator.living_doc_generator import MdocLivingDocumentationGenerator
from living_doc_generator.mdoc_exporter import MdocExporter
from living_doc_utilities.model.feature_issue import FeatureIssue
from living_doc_utilities.model.functionality_issue import FunctionalityIssue
from living_doc_utilities.model.issues import Issues
from living_doc_utilities.model.project_status import ProjectStatus
from living_doc_utilities.model.user_story_issue import UserStoryIssue


@pytest.fixture
def load_all_templates_setup(mocker):
    mock_load_all_templates = mocker.patch.object(
        MdocLivingDocumentationGenerator,
        "_load_all_templates",
        return_value=(
            "Issue Page Template",
            "Index Page Template",
            "Root Level Page Template",
            "Org Level Template",
            "Repo Page Template",
            "Data Level Template",
            "Report Page Template",
        ),
    )

    return mock_load_all_templates


@pytest.fixture
def mdoc_exporter(tmp_path):
    """Fixture to create an instance of MdocExporter with modified template paths."""
    output_dir = os.path.join(tmp_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    return MdocExporter(output_dir)


@pytest.fixture
def sample_issues_without_project_states():
    issues: Issues = Issues()

    issue_us_1: UserStoryIssue = UserStoryIssue()
    issue_us_1.repository_id = "org/repo"
    issue_us_1.issue_number = 1
    issue_us_1.title = "Sample User Story 1"
    issue_us_1.body = "This is a sample user story issue body."
    issue_us_1.state = "In Progress"
    issue_us_2: UserStoryIssue = UserStoryIssue()
    issue_us_2.repository_id = "org/repo"
    issue_us_2.issue_number = 2
    issue_us_2.title = "Sample User Story 2"
    issue_us_2.body = "This is another sample user story issue body."
    issue_us_2.state = "To Do"
    issue_feat_1: FeatureIssue = FeatureIssue()
    issue_feat_1.repository_id = "org/repo"
    issue_feat_1.issue_number = 3
    issue_feat_1.title = "Sample Feature 1"
    issue_feat_1.body = "This is a sample feature issue body."
    issue_feat_1.state = "In Progress"
    issue_feat_2: FeatureIssue = FeatureIssue()
    issue_feat_2.repository_id = "org/repo"
    issue_feat_2.issue_number = 4
    issue_feat_2.title = "Sample Feature 2"
    issue_feat_2.body = "This is a sample feature issue body."
    issue_feat_2.state = "To Do"
    issue_func_1: FunctionalityIssue = FunctionalityIssue()
    issue_func_1.repository_id = "org/repo"
    issue_func_1.issue_number = 5
    issue_func_1.title = "Sample Functionality 1"
    issue_func_1.body = "This is a sample function issue body.\n### Associated Feature\n- #3\n"
    issue_func_1.state = "In Progress"
    issue_func_2: FunctionalityIssue = FunctionalityIssue()
    issue_func_2.repository_id = "org/repo"
    issue_func_2.issue_number = 6
    issue_func_2.title = "Sample Functionality 2"
    issue_func_2.body = "This is a sample function issue body.\n### Associated Feature\n- #4\n"
    issue_func_2.state = "To Do"

    issues.issues["org/repo/1"] = issue_us_1
    issues.issues["org/repo/2"] = issue_us_2
    issues.issues["org/repo/3"] = issue_feat_1
    issues.issues["org/repo/4"] = issue_feat_2
    issues.issues["org/repo/5"] = issue_func_1
    issues.issues["org/repo/6"] = issue_func_2

    return issues

@pytest.fixture
def sample_issues_with_project_states(sample_issues_without_project_states):
    prj_status_in_progress = ProjectStatus()
    prj_status_in_progress.status = "In Progress"
    prj_status_todo = ProjectStatus()
    prj_status_todo.status = "To Do"

    sample_issues_without_project_states.issues["org/repo/1"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/1"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/2"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/2"].project_statuses.append(prj_status_todo)
    sample_issues_without_project_states.issues["org/repo/3"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/3"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/4"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/4"].project_statuses.append(prj_status_todo)
    sample_issues_without_project_states.issues["org/repo/5"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/5"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/6"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/6"].project_statuses.append(prj_status_todo)

    sample_issues_without_project_states.project_states_included = True

    return sample_issues_without_project_states


@pytest.fixture
def sample_issues_with_errors_without_project_states(sample_issues_without_project_states):
    sample_issues_without_project_states.get_issue("org/repo/1").add_errors({"SomeError": "Fake some error."})
    sample_issues_without_project_states.get_issue("org/repo/2").add_errors({"SomeError": "Fake some error."})
    return sample_issues_without_project_states


@pytest.fixture
def sample_issues_with_errors_with_project_states(sample_issues_with_project_states):
    sample_issues_with_project_states.get_issue("org/repo/1").add_errors({"SomeError": "Fake some error."})
    sample_issues_with_project_states.get_issue("org/repo/2").add_errors({"SomeError": "Fake some error."})
    return sample_issues_with_project_states
