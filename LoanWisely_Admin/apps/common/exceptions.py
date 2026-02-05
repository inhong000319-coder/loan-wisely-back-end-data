class UnauthorizedError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class UpstreamError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
