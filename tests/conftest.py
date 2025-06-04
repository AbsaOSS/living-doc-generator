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

from living_doc_generator.living_doc_generator import MdocLivingDocumentationGenerator


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


# @pytest.fixture
# def living_documentation_generator(mocker):
#     mock_github_class = mocker.patch("living_documentation_regime.living_documentation_generator.Github")
#     mock_github_instance = mock_github_class.return_value
#
#     mock_rate_limit = mocker.Mock()
#     mock_rate_limit.remaining = 5000
#     mock_rate_limit.reset = datetime.datetime.now() + datetime.timedelta(minutes=10)
#
#     mock_github_instance.get_rate_limit.return_value = mocker.Mock(core=mock_rate_limit)
#     mock_github_instance.get_repo.return_value = mocker.Mock()
#
#     mocker.patch(
#         "living_documentation_regime.living_documentation_generator.ActionInputs.get_github_token",
#         return_value="FakeGithubToken",
#     )
#     return MdocLivingDocumentationGenerator(make_absolute_path(OUTPUT_PATH))
