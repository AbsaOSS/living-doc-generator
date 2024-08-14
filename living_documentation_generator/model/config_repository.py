class ConfigRepository:
    """
    A class representing the configuration for a GH repository to fetch data from.

    Attributes:
        __organization_name (str): The name of the organization that owns the repository.
        __repository_name (str): The name of the repository.
        __query_labels (list[str | None]): List of labels to query for.
        __projects_title_filter (list[str | None]): List of project titles to filter for.
    """
    def __init__(self):
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__query_labels: list[str | None] = [None]
        self.__projects_title_filter: list[str | None] = [None]

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def query_labels(self) -> list[str]:
        return self.__query_labels if self.__query_labels is not None else []

    @property
    def projects_title_filter(self) -> list[str]:
        return (
            self.__projects_title_filter
            if self.__projects_title_filter is not None
            else []
        )

    def load_from_json(self, repository_json: dict):
        self.__organization_name = repository_json["organization-name"]
        self.__repository_name = repository_json["repository-name"]
        self.__query_labels = repository_json["query-labels"]
        self.__projects_title_filter = repository_json["projects-title-filter"]
