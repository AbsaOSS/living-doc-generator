from living_documentation_generator.utils.constants import NO_PROJECT_DATA


class ProjectStatus:
    def __init__(self):
        self.__project_title: str = ""
        self.__status: str = NO_PROJECT_DATA
        self.__priority: str = NO_PROJECT_DATA
        self.__size: str = NO_PROJECT_DATA
        self.__moscow: str = NO_PROJECT_DATA

    @property
    def project_title(self) -> str:
        return self.__project_title

    @project_title.setter
    def project_title(self, value: str):
        self.__project_title = value

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, value: str):
        self.__status = value

    @property
    def priority(self) -> str:
        return self.__priority

    @priority.setter
    def priority(self, value: str):
        self.__priority = value

    @property
    def size(self) -> str:
        return self.__size

    @size.setter
    def size(self, value: str):
        self.__size = value

    @property
    def moscow(self) -> str:
        return self.__moscow

    @moscow.setter
    def moscow(self, value: str):
        self.__moscow = value
