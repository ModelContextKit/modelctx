"""Custom exceptions for ModelCtx."""

from typing import Optional, Dict, Any


class ModelCtxError(Exception):
    """Base exception class for ModelCtx operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class BackendError(ModelCtxError):
    """Exception raised for backend-related errors."""
    pass


class ConfigurationError(ModelCtxError):
    """Exception raised for configuration-related errors."""
    pass


class ValidationError(ModelCtxError):
    """Exception raised for validation errors."""
    pass


class ProjectGenerationError(ModelCtxError):
    """Exception raised during project generation."""
    pass


class DependencyError(ModelCtxError):
    """Exception raised for dependency-related errors."""
    pass


class TemplateError(ModelCtxError):
    """Exception raised for template-related errors."""
    pass