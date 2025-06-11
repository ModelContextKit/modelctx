"""Backend implementations for MCP server generation."""

from typing import Dict, Type
from modelctx.backends.base import BaseBackend

# Import all backend implementations
from modelctx.backends.database import DatabaseBackend
from modelctx.backends.api import APIBackend
from modelctx.backends.filesystem import FilesystemBackend
from modelctx.backends.webscraper import WebScraperBackend
from modelctx.backends.email import EmailBackend
from modelctx.backends.cloudstorage import CloudStorageBackend

AVAILABLE_BACKENDS: Dict[str, Type[BaseBackend]] = {}

def register_backend(backend_class: Type[BaseBackend]) -> None:
    """Register a backend class."""
    backend_type = backend_class.get_backend_type()
    AVAILABLE_BACKENDS[backend_type] = backend_class

def get_backend_class(backend_type: str) -> Type[BaseBackend]:
    """Get backend class by type."""
    if backend_type not in AVAILABLE_BACKENDS:
        raise ValueError(f"Unknown backend type: {backend_type}")
    return AVAILABLE_BACKENDS[backend_type]

def list_backends() -> Dict[str, str]:
    """List all available backends with descriptions."""
    return {
        backend_type: backend_class.get_description()
        for backend_type, backend_class in AVAILABLE_BACKENDS.items()
    }

# Register all available backends
register_backend(DatabaseBackend)
register_backend(APIBackend)
register_backend(FilesystemBackend)
register_backend(WebScraperBackend)
register_backend(EmailBackend)
register_backend(CloudStorageBackend)

__all__ = [
    "BaseBackend", 
    "DatabaseBackend",
    "APIBackend", 
    "FilesystemBackend",
    "WebScraperBackend",
    "EmailBackend",
    "CloudStorageBackend",
    "AVAILABLE_BACKENDS", 
    "register_backend", 
    "get_backend_class", 
    "list_backends"
]