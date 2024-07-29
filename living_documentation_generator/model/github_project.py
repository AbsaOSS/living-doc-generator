from living_documentation_generator.model.config_repository import ConfigRepository


class GithubProject:
    def __init__(self):
        self.__id: str = ""
        self.__number: int = 0
        self.__title: str = ""
        self.__organization_name: str = ""
        self.__config_repositories: list[ConfigRepository] = []
        self.__field_options: dict[str, str] = {}

    @property
    def id(self) -> str:
        return self.__id

    @property
    def number(self) -> int:
        return self.__number

    @property
    def title(self) -> str:
        return self.__title

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    # TODO - method not used - is that needed?
    @property
    def config_repositories(self) -> list[ConfigRepository]:
        return self.__config_repositories

    @property
    def field_options(self) -> dict[str, str]:
        return self.__field_options

    def load_from_json(self, project_json, repository):
        self.__id = project_json["id"]
        self.__number = project_json["number"]
        self.__title = project_json["title"]
        self.__organization_name = repository.owner.login
        self.__config_repositories.append(repository.name)

        return self
