from typing import Optional, Any


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", code: str = "UNAUTHORIZED", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=401, details=details)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", code: str = "FORBIDDEN", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=403, details=details)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=404, details=details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", code: str = "CONFLICT", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=409, details=details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=422, details=details)
