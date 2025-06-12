"""Error handling utilities and decorators for ModelCtx."""

import functools
import json
import logging
from typing import Any, Callable, Dict, List, TypeVar, Union, Optional

try:
    from mcp.types import TextContent
except ImportError:
    # Handle case where mcp is not installed
    TextContent = None

from modelctx.exceptions import ModelCtxError, BackendError, ValidationError
from modelctx.utils.logging import get_logger

logger = get_logger("error_handling")

F = TypeVar('F', bound=Callable[..., Any])


def handle_backend_errors(func: F) -> F:
    """Decorator for consistent backend error handling.
    
    Catches exceptions and returns standardized MCP error responses.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BackendError as e:
            logger.error(f"Backend error in {func.__name__}: {e}")
            return _create_error_response(str(e), "backend_error", e.details)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return _create_error_response(
                f"Unexpected error: {str(e)}", 
                "internal_error"
            )
    
    return wrapper


def handle_validation_errors(func: F) -> F:
    """Decorator for validation error handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError) as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise ValidationError(str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


def _create_error_response(
    message: str, 
    error_type: str = "error",
    details: Optional[Dict[str, Any]] = None
) -> List[Any]:
    """Create a standardized error response for MCP tools.
    
    Args:
        message: Error message
        error_type: Type of error
        details: Additional error details
    
    Returns:
        List containing TextContent with error response (or dict if MCP not available)
    """
    error_data = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message
        }
    }
    
    if details:
        error_data["error"]["details"] = details
    
    if TextContent is not None:
        return [TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]
    else:
        # Fallback when MCP is not available
        return [{"type": "text", "text": json.dumps(error_data, indent=2)}]


def format_cli_error(message: str, suggestion: Optional[str] = None) -> str:
    """Format error message for CLI display.
    
    Args:
        message: Error message
        suggestion: Optional suggestion for fixing the error
    
    Returns:
        Formatted error message
    """
    formatted = f"[red]ERROR: {message}[/red]"
    if suggestion:
        formatted += f"\n[yellow]Suggestion: {suggestion}[/yellow]"
    return formatted


def format_cli_warning(message: str) -> str:
    """Format warning message for CLI display.
    
    Args:
        message: Warning message
    
    Returns:
        Formatted warning message
    """
    return f"[yellow]WARNING: {message}[/yellow]"


def format_cli_success(message: str) -> str:
    """Format success message for CLI display.
    
    Args:
        message: Success message
    
    Returns:
        Formatted success message
    """
    return f"[green]SUCCESS: {message}[/green]"


class ErrorCollector:
    """Utility class for collecting and managing multiple errors."""
    
    def __init__(self):
        self.errors: List[ModelCtxError] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: Union[str, ModelCtxError], **details):
        """Add an error to the collection."""
        if isinstance(error, str):
            error = ModelCtxError(error, details)
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning to the collection."""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages as strings."""
        return [str(error) for error in self.errors]
    
    def get_summary(self) -> str:
        """Get a summary of all errors and warnings."""
        summary = []
        
        if self.errors:
            summary.append(f"Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                summary.append(f"  {i}. {error}")
        
        if self.warnings:
            summary.append(f"Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                summary.append(f"  {i}. {warning}")
        
        return "\n".join(summary) if summary else "No errors or warnings"
    
    def clear(self):
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()