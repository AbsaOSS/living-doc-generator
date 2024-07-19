import json
import logging
import os

from living_documentation_generator.action.model.config_repository import ConfigRepository
from living_documentation_generator.utils import make_absolute_path


class ActionInputs:
    def __init__(self):
        self.__github_token: str = ""
        self.__is_project_state_mining_enabled: bool = False
        self.__projects_title_filter: list = []
        self.__repositories: list[ConfigRepository] = []
        self.__output_directory: str = ""

    @property
    def github_token(self) -> str:
        return self.__github_token

    @property
    def is_project_state_mining_enabled(self) -> bool:
        return self.__is_project_state_mining_enabled

    @property
    def projects_title_filter(self) -> list:
        return self.__projects_title_filter

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self.__repositories

    @property
    def output_directory(self) -> str:
        return self.__output_directory

    def load_from_environment(self, validate: bool = True) -> 'ActionInputs':
        self.__github_token = os.getenv('GITHUB_TOKEN')
        self.__is_project_state_mining_enabled = os.getenv('PROJECT_STATE_MINING', "false").lower() == "true"
        self.__projects_title_filter = os.getenv('PROJECTS_TITLE_FILTER')
        out_path = os.getenv('OUTPUT_PATH', './output')
        self.__output_directory = make_absolute_path(out_path)
        repositories_json = os.getenv('REPOSITORIES')

        logging.debug(f'Is project state mining allowed: {self.is_project_state_mining_enabled}')
        logging.debug(f'Project title filter: {self.projects_title_filter}')
        logging.debug(f'Json repositories to fetch from: {repositories_json}')
        logging.debug(f'Output directory: {self.output_directory}')

        # Validate inputs
        if validate:
            self.validate_inputs(repositories_json)

        # Parse repositories json string into json dictionary format
        try:
            repositories_json = json.loads(repositories_json)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing json repositories: {e}")
            exit(1)

        for repository_json in repositories_json:
            config_repository = ConfigRepository()
            config_repository.load_from_json(repository_json)
            self.__repositories.append(config_repository)

        return self

    def validate_inputs(self, repositories_json: str) -> None:
        # Validate correct format of input repositories_json
        try:
            json.loads(repositories_json)
        except json.JSONDecodeError:
            raise ValueError("Input attr `repositories_json` is not a valid JSON string")

        # Validate GitHub token
        if not self.__github_token:
            raise ValueError("GitHub token could not be loaded from the environment")
