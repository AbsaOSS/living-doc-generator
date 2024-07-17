from github_integration.model.github_project import GithubProject


class ProjectIssue:
    def __init__(self):
        # TODO: I dont know which attributes I want in my final class
        self.__number: int = 0
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__project_name: str = ""
        # self.__project_repositories: list[str] = []
        self.__status: str = "N/A"
        self.__priority: str = "N/A"
        self.__size: str = "N/A"
        self.__moscow: str = "N/A"

    @property
    def number(self) -> int:
        return self.__number

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def project_repositories(self) -> list[str]:
        return self.__project_repositories

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

    def load_from_json(self, issue_json: dict, project: GithubProject):
        self.__number = issue_json["content"]["number"]
        self.__organization_name = issue_json["content"]["repository"]["owner"]["login"]
        self.__repository_name = issue_json["content"]["repository"]["name"]
        self.__project_name = project.title
        # self.__project_repositories = project.project_repositories

        field_types = []
        if 'fieldValues' in issue_json:
            for node in issue_json['fieldValues']['nodes']:
                if node['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                    field_types.append(node['name'])

        for field_type in field_types:
            if field_type in project.field_options.get('Status', []):
                self.__status = field_type
            elif field_type in project.field_options.get('Priority', []):
                self.__priority = field_type
            elif field_type in project.field_options.get('Size', []):
                self.__size = field_type
            elif field_type in project.field_options.get('MoSCoW', []):
                self.__moscow = field_type

        return self

    def to_dict(self):
        return {
            "number": self.__number,
            "organization_name": self.__organization_name,
            "repository_name": self.__repository_name,
            "project_name": self.__project_name,
            "status": self.__status,
            "priority": self.__priority,
            "size": self.__size,
            "moscow": self.__moscow
        }
