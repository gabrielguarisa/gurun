class GurunException(Exception):
    """
    Base class for all exceptions in Gurun.
    """

    pass


class RunnerException(GurunException):
    """
    Raised when something goes wrong with the runner.
    """

    pass


class GurunTypeError(GurunException, TypeError):
    """
    Raised when a type error occurs.
    """

    def __init__(self, var_name: str, expected_type: str, received_type: str) -> None:
        super().__init__(f"{var_name} must be {expected_type}, got {received_type}")
