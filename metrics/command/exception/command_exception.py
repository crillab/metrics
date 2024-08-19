import sys

import loguru


class CommandError(Exception):
    """General exception for errors related to a Command."""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self._exit_code = exit_code

    def handle(self):
        loguru.logger.error(self)
        sys.exit(self._exit_code)


class BinaryVersionNotFoundError(CommandError):
    """Exception raised when the specified version is not found."""

    def __init__(self):
        super().__init__("Version not found.", 2)


class BinaryDuplicateVersionError(CommandError):
    """Exception raised when multiple versions are found."""
    pass


class BinaryBuildError(CommandError):
    """Exception raised in case of an error during the build process."""
    pass


class BinaryPathExistsError(CommandError):
    """Exception raised if the path already exists when adding an experiment ware."""
    pass
