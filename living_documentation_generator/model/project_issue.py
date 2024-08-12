from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.utils.constants import Constants


# pylint: disable=too-many-instance-attributes
class ProjectIssue:
    def __init__(self):
        self.__number: int = 0
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__project_name: str = ""
        self.__status: str = Constants.NOT_AVAILABLE
        self.__priority: str = Constants.NOT_AVAILABLE
        self.__size: str = Constants.NOT_AVAILABLE
        self.__moscow: str = Constants.NOT_AVAILABLE

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
