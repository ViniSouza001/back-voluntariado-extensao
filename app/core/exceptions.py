class ApplicationError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class AuthenticationError(ApplicationError):
    status_code = 401


class NotFoundError(ApplicationError):
    status_code = 404


class ConflictError(ApplicationError):
    status_code = 409


class ValidationError(ApplicationError):
    status_code = 422
