from uuid import UUID

from fastapi import HTTPException


class ExternalServiceError(HTTPException):
    """Base class for errors related to external services."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ExternalServiceNotFoundError(ExternalServiceError):
    """Raised when a resource is not found in an external service."""
    def __init__(self, resource_name: str, resource_id: str | int, service_name: str = "internal service"):
        detail = f"{resource_name.capitalize()} '{resource_id}' not found in {service_name}."
        super().__init__(status_code=404, detail=detail)

class ExternalServiceConnectionError(ExternalServiceError):
    """Raised when there's a connection issue with an external service."""
    def __init__(self, service_name: str = "internal service", original_error: Exception | None = None):
        detail = f"Could not connect to {service_name}."
        if original_error:
            detail += f" Original error: {str(original_error)}"
        super().__init__(status_code=503, detail=detail)

class ExternalServiceUnexpectedError(ExternalServiceError):
    """Raised for other unexpected errors from an external service."""
    def __init__(self, service_name: str = "internal service", original_error: Exception | None = None):
        detail = f"An unexpected error occurred while communicating with {service_name}."
        if original_error:
            detail += f" Original error: {str(original_error)}"
        super().__init__(status_code=500, detail=detail)


class ServerInitError(HTTPException):
    def __init__(self, code:int = 500, message:str = ''):
        super().__init__(status_code=code, detail=f"Server's Lifespan Init Error, \n {message}")

class CriticalDependencyError(ServerInitError):
    def __init__(self, service_name: str, original_error: Exception | None = None):
        message = f"Failed to connect to or initialize critical dependency: {service_name}."
        if original_error:
            message += f" Original error: {str(original_error)}"
        super().__init__(code=503, message=message)

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)\

class ValueNotFoundError(HTTPException):
    def __init__(self, event_id: int | UUID):
        detail = f"Event with ID '{str(event_id)}' not found or data missing"
        super().__init__(status_code=404, detail=detail)
