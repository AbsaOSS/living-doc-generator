import json
import logging

from living_documentation_generator.model.config_repository import ConfigRepository
from living_documentation_generator.utils.utils import get_action_input, make_absolute_path
from living_documentation_generator.utils.constants import Constants

logger = logging.getLogger(__name__)


class ActionInputs:

    def __init__(self):
        self.__github_token: str = ""
        self.__is_project_state_mining_enabled: bool = False
        self.__repositories: list[ConfigRepository] = []
        self.__output_directory: str = ""

    @property
    def github_token(self) -> str:
        return self.__github_token

    @property
    def is_project_state_mining_enabled(self) -> bool:
        return self.__is_project_state_mining_enabled

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self.__repositories

    @property
    def output_directory(self) -> str:
        return self.__output_directory

    def load_from_environment(self, validate: bool = True) -> 'ActionInputs':
        self.__github_token = get_action_input(Constants.GITHUB_TOKEN)
        self.__is_project_state_mining_enabled = get_action_input(Constants.PROJECT_STATE_MINING, "false").lower() == "true"
        out_path = get_action_input(Constants.OUTPUT_PATH, './output')
        self.__output_directory = make_absolute_path(out_path)
        repositories_json = get_action_input(Constants.REPOSITORIES, "")

        logger.debug('Is project state mining allowed: %s.', self.is_project_state_mining_enabled)
        logger.debug('JSON repositories to fetch from: %s.', repositories_json)
        logger.debug('Output directory: %s.', self.output_directory)

        # Validate inputs
        if validate:
            self.validate_inputs(repositories_json)

        # Parse repositories json string into json dictionary format
        try:
            repositories_json = json.loads(repositories_json)
        except json.JSONDecodeError as e:
            logger.error("Error parsing JSON repositories: %s.", e, exc_info=True)
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
            logger.error("Input attr `repositories_json` is not a valid JSON string.", exc_info=True)
            exit(1)

        # Validate GitHub token
        if not self.__github_token:
            logger.error("GitHub token could not be loaded from the environment.", exc_info=True)
            exit(1)
