import logging

from living_documentation_generator.model.config_repository import ConfigRepository

logger = logging.getLogger(__name__)


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

    @property
    def field_options(self) -> dict[str, str]:
        return self.__field_options

    def load_from_json(self, project_json, repository, field_option_response):
        self.__id = project_json["id"]
        self.__number = project_json["number"]
        self.__title = project_json["title"]
        self.__organization_name = repository.owner.login
        self.__config_repositories.append(repository.name)

        logger.debug(
            "Updating field options for projects in repository `%s`.",
            repository.full_name,
        )
        self.__update_field_options(field_option_response)

        return self

    def __update_field_options(self, field_option_response: dict):
        # Parse the field options from the response
        field_options_nodes = field_option_response["repository"]["projectV2"][
            "fields"
        ]["nodes"]
        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the project structure with field options
                self.field_options.update({field_name: options})
