from living_documentation_generator.utils.constants import (
    PROJECTS_FROM_REPO_QUERY,
    ISSUES_FROM_PROJECT_QUERY,
    PROJECT_FIELD_OPTIONS_QUERY,
    ISSUES_PER_PAGE_LIMIT,
)


class GithubProjectQueries:
    """
    A class containing format methods for the GitHub GraphQL queries.
    """
    @staticmethod
    def get_projects_from_repo_query(
        organization_name: str, repository_name: str
    ) -> str:
        return PROJECTS_FROM_REPO_QUERY.format(
            organization_name=organization_name, repository_name=repository_name
        )

    @staticmethod
    def get_issues_from_project_query(project_id: str, after_argument: str) -> str:
        return ISSUES_FROM_PROJECT_QUERY.format(
            project_id=project_id,
            issues_per_page=ISSUES_PER_PAGE_LIMIT,
            after_argument=after_argument,
        )

    @staticmethod
    def get_project_field_options_query(
        organization_name: str, repository_name: str, project_number: int
    ) -> str:
        return PROJECT_FIELD_OPTIONS_QUERY.format(
            organization_name=organization_name,
            repository_name=repository_name,
            project_number=project_number,
        )
