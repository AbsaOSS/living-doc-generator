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

"""
This module contains the LivingDocumentationGenerator class which is responsible for generating
the Living Documentation output.
"""

import logging
import os
import shutil
from typing import Callable

from github import Github, Auth
from github.Issue import Issue

from factory.exporter_factory import ExporterFactory
from action_inputs import ActionInputs
from living_documentation_regime.github_projects import GithubProjects
from living_documentation_regime.model.github_project import GithubProject
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from living_documentation_regime.model.project_issue import ProjectIssue
from utils.decorators import safe_call_decorator
from utils.github_rate_limiter import GithubRateLimiter
from utils.utils import make_issue_key
from utils.constants import (
    ISSUES_PER_PAGE_LIMIT,
    ISSUE_STATE_ALL,
    Regime,
)

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class LivingDocumentationGenerator:
    """
    A class representing the Living Documentation Generator.
    The class uses several helper methods to fetch required data from GitHub, consolidate the data
    and generate the output in required format as the output of action's Living Documentation regime.
    """

    def __init__(self, output_path: str):
        github_token = ActionInputs.get_github_token()

        self.__regime_output_path = os.path.join(output_path, "liv-doc-regime")
        self.__github_instance: Github = Github(auth=Auth.Token(token=github_token), per_page=ISSUES_PER_PAGE_LIMIT)
        self.__github_projects_instance: GithubProjects = GithubProjects(token=github_token)
        self.__rate_limiter: GithubRateLimiter = GithubRateLimiter(self.__github_instance)
        self.__safe_call: Callable = safe_call_decorator(self.__rate_limiter)

    def generate(self) -> bool:
        """
        Generate the Living Documentation Regime output.

        @return: True if generation is successful, False otherwise (error occurred).
        """
        self._clean_output_directory()
        logger.debug("Regime's 'LivDoc' output directory cleaned.")

        # Data mine GitHub issues with defined labels from all repositories
        logger.info("Fetching repository GitHub issues - started.")
        repository_issues: dict[str, list[Issue]] = self._fetch_github_issues()
        # Note: got dict of list of issues for each repository (key is repository id)
        logger.info("Fetching repository GitHub issues - finished.")

        # Data mine GitHub project's issues
        logger.info("Fetching GitHub project data - started.")
        project_issues: dict[str, list[ProjectIssue]] = self._fetch_github_project_issues()
        # Note: got dict of project issues with unique string key defying the issue
        logger.info("Fetching GitHub project data - finished.")

        # Consolidate all issue data together
        logger.info("Issue and project data consolidation - started.")
        consolidated_issues: dict[str, ConsolidatedIssue] = self._consolidate_issues_data(
            repository_issues, project_issues
        )
        logger.info("Issue and project data consolidation - finished.")

        # Generate markdown pages
        return self._generate_living_documents(consolidated_issues)

    def _clean_output_directory(self) -> None:
        """
        Clean the output directory from the previous run.

        @return: None
        """
        if os.path.exists(self.__regime_output_path):
            shutil.rmtree(self.__regime_output_path)
        os.makedirs(self.__regime_output_path)

    def _fetch_github_issues(self) -> dict[str, list[Issue]]:
        """
        Fetch GitHub repository issues using the GitHub library. Only issues with correct labels are fetched,
        if no labels are defined in the configuration, all repository issues are fetched.

        @return: A dictionary containing repository issue objects with unique key.
        """
        issues = {}
        total_issues_number = 0

        # Run the fetching logic for every config repository
        # Here is no need for catching exception, because get_repositories
        # is static and it was handle when validating user configuration.
        for config_repository in ActionInputs.get_repositories():
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"

            repository = self.__safe_call(self.__github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            logger.info("Fetching repository GitHub issues - from `%s`.", repository.full_name)

            # If the query labels are not defined, fetch all issues from the repository
            if not config_repository.query_labels:
                logger.debug("Fetching all issues in the repository")
                issues[repository_id] = self.__safe_call(repository.get_issues)(state=ISSUE_STATE_ALL)
                amount_of_issues_per_repo = len(list(issues[repository_id]))
                logger.debug(
                    "Fetched `%i` repository issues (%s)`.",
                    amount_of_issues_per_repo,
                    repository.full_name,
                )
            else:
                # Fetch only issues with required labels from configuration
                issues[repository_id] = []
                logger.debug("Labels to be fetched from: %s.", config_repository.query_labels)
                for label in config_repository.query_labels:
                    logger.debug("Fetching issues with label `%s`.", label)
                    issues[repository_id].extend(
                        self.__safe_call(repository.get_issues)(state=ISSUE_STATE_ALL, labels=[label])
                    )
                amount_of_issues_per_repo = len(issues[repository_id])

            # Accumulate the count of issues
            total_issues_number += amount_of_issues_per_repo
            logger.info(
                "Fetching repository GitHub issues - fetched `%i` repository issues (%s).",
                amount_of_issues_per_repo,
                repository.full_name,
            )

        logger.info(
            "Fetching repository GitHub issues - loaded `%i` repository issues in total.",
            total_issues_number,
        )
        return issues

    def _fetch_github_project_issues(self) -> dict[str, list[ProjectIssue]]:
        """
        Fetch GitHub project issues using the GraphQL API.

        @return: A dictionary containing project issue objects with unique key.
        """
        if not ActionInputs.is_project_state_mining_enabled():
            logger.info("Fetching GitHub project data - project mining is not allowed.")
            return {}

        logger.debug("Project data mining allowed.")

        # Mine project issues for every repository
        all_project_issues: dict[str, list[ProjectIssue]] = {}

        # Here is no need for catching exception, because get_repositories
        # is static and it was handle when validating user configuration.
        for config_repository in ActionInputs.get_repositories():
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"
            projects_title_filter = config_repository.projects_title_filter
            logger.debug("Filtering projects: %s. If filter is empty, fetching all.", projects_title_filter)

            repository = self.__safe_call(self.__github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            # Fetch all projects_buffer attached to the repository
            logger.debug("Fetching GitHub project data - looking for repository `%s` projects.", repository_id)
            projects: list[GithubProject] = self.__safe_call(self.__github_projects_instance.get_repository_projects)(
                repository=repository, projects_title_filter=projects_title_filter
            )

            if projects:
                logger.info(
                    "Fetching GitHub project data - for repository `%s` found `%i` project/s.",
                    repository.full_name,
                    len(projects),
                )
            else:
                logger.info(
                    "Fetching GitHub project data - no project data found for repository `%s`.", repository.full_name
                )

            # Update every project with project issue related data
            for project in projects:
                logger.info("Fetching GitHub project data - fetching project data from `%s`.", project.title)
                project_issues: list[ProjectIssue] = self.__safe_call(
                    self.__github_projects_instance.get_project_issues
                )(project=project)

                for project_issue in project_issues:
                    key = make_issue_key(
                        project_issue.organization_name,
                        project_issue.repository_name,
                        project_issue.number,
                    )

                    # If the key is unique, add the project issue to the dictionary
                    if key not in all_project_issues:
                        all_project_issues[key] = [project_issue]
                    else:
                        # If the project issue key is already present, add another project data from other projects
                        all_project_issues[key].append(project_issue)
                logger.info(
                    "Fetching GitHub project data - successfully fetched project data from `%s`.", project.title
                )

        return all_project_issues

    @staticmethod
    def _consolidate_issues_data(
        repository_issues: dict[str, list[Issue]], project_issues: dict[str, list[ProjectIssue]]
    ) -> dict[str, ConsolidatedIssue]:
        """
        Consolidate the fetched issues and extra project data into a one consolidated object.

        @param repository_issues: A dictionary containing repository issue objects with unique key.
        @param project_issues: A dictionary containing project issue objects with unique key.
        @return: A dictionary containing all consolidated issues.
        """

        consolidated_issues = {}

        # Create a ConsolidatedIssue object for each repository issue
        for repository_id in repository_issues.keys():
            for repository_issue in repository_issues[repository_id]:
                repo_id_parts = repository_id.split("/")
                unique_key = make_issue_key(repo_id_parts[0], repo_id_parts[1], repository_issue.number)
                consolidated_issues[unique_key] = ConsolidatedIssue(
                    repository_id=repository_id, repository_issue=repository_issue
                )

        # Update consolidated issue structures with project data
        logger.debug("Updating consolidated issue structure with project data.")
        for key, consolidated_issue in consolidated_issues.items():
            if key in project_issues:
                for project_issue in project_issues[key]:
                    consolidated_issue.update_with_project_data(project_issue.project_status)

        logger.info(
            "Issue and project data consolidation - consolidated `%i` repository issues with extra project data.",
            len(consolidated_issues),
        )
        return consolidated_issues

    def _generate_living_documents(self, issues: dict[str, ConsolidatedIssue]) -> bool:
        """
        Generate the output in the required formats.

        @param issues: A dictionary containing all consolidated issues.
        @return: True if generation is successful, False otherwise (error occurred).
        """
        statuses: list[bool] = []

        for output_format in ActionInputs.get_liv_doc_output_formats():
            exporter = ExporterFactory.get_exporter(Regime.LIV_DOC_REGIME, output_format, self.__regime_output_path)
            if exporter is not None:
                statuses.append(exporter.export(issues=issues))
            else:
                logger.error("No generation process for this format: %s", output_format)
                statuses.append(False)

        if all(statuses):
            logger.info("Living Documentation output generated successfully.")
            return True

        logger.error("Living Documentation output generation failed.")
        return False
