from living_documentation_generator.utils.constants import Constants


def get_projects_from_repo_query(organization_name: str, repository_name: str) -> str:
    return Constants.PROJECTS_FROM_REPO_QUERY.format(organization_name=organization_name,
                                                     repository_name=repository_name)


def get_issues_from_project_query(project_id: str, after_argument: str) -> str:
    return Constants.ISSUES_FROM_PROJECT_QUERY.format(project_id=project_id,
                                                      issues_per_page=Constants.ISSUES_PER_PAGE_LIMIT,
                                                      after_argument=after_argument)


def get_project_field_options_query(organization_name: str, repository_name: str, project_number: int) -> str:
    return Constants.PROJECT_FIELD_OPTIONS_QUERY.format(organization_name=organization_name,
                                                        repository_name=repository_name,
                                                        project_number=project_number)
