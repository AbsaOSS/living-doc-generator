from github.Issue import Issue

from living_documentation_generator.model.project_issue import ProjectIssue
from living_documentation_generator.utils.utils import sanitize_filename

NOT_SET_FOR_NOW = "NOT_SET_IN_THIS_VERSION"
NO_PROJECT_ATTACHED = "---"
NO_PROJECT_MINING = "-?-"


class ConsolidatedIssue:
    def __init__(self, repository_id: str, repository_issue: Issue = None):
        # save issue from repository (got from Github library & keep connection to repository for lazy loading)
        # Warning: several issue properties requires additional API calls - use wisely to keep low API usage
        self.__issue = repository_issue

        parts = repository_id.split("/")
        self.__organization_name: str = parts[0] if len(parts) == 2 else ""
        self.__repository_name: str = parts[1] if len(parts) == 2 else ""

        # Extra project data (optionally provided from GithubProjects class)
        self.__linked_to_project: bool = False
        self.__project_name: str = NO_PROJECT_ATTACHED
        self.__status: str = NO_PROJECT_ATTACHED
        self.__priority: str = NO_PROJECT_ATTACHED
        self.__size: str = NO_PROJECT_ATTACHED
        self.__moscow: str = NO_PROJECT_ATTACHED

        self.__error: str | None = None

    @property
    def number(self) -> int:
        return self.__issue.number if self.__issue else 0

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def title(self) -> str:
        return self.__issue.title if self.__issue else ""

    @property
    def state(self) -> str:
        return self.__issue.state if self.__issue else ""

    @property
    def url(self) -> str:
        return self.__issue.url if self.__issue else ""

    @property
    def body(self) -> str:
        return self.__issue.body if self.__issue else ""

    @property
    def labels(self) -> list[str]:
        if self.__issue:
            return [label.name for label in self.__issue.labels]
        else:
            return []

    @property
    def linked_to_project(self) -> bool:
        return self.__linked_to_project

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def status(self) -> str:
        return self.__status

    @property
    def priority(self) -> str:
        return self.__priority

    @property
    def size(self) -> str:
        return self.__size

    @property
    def moscow(self) -> str:
        return self.__moscow

    @property
    def error(self) -> str | None:
        return self.__error

    def update_with_project_data(self, issue: ProjectIssue):
        self.__linked_to_project = True
        self.__project_name = issue.project_name
        self.__status = issue.status
        self.__priority = issue.priority
        self.__size = issue.size
        self.__moscow = issue.moscow

    def no_project_mining(self):
        self.__project_name = NO_PROJECT_MINING
        self.__status = NO_PROJECT_MINING
        self.__priority = NO_PROJECT_MINING
        self.__size = NO_PROJECT_MINING
        self.__moscow = NO_PROJECT_MINING

        return self

    def generate_page_filename(self):
        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        page_filename = sanitize_filename(md_filename_base)

        return page_filename
