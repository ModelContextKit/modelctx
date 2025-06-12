"""Backend registry for managing available backends."""

from typing import Dict, List, Type
from modelctx.backends.base import BaseBackend
from modelctx.backends import AVAILABLE_BACKENDS


class BackendRegistry:
    """Registry for managing and validating available backends."""
    
    def __init__(self) -> None:
        self._backends: Dict[str, Type[BaseBackend]] = AVAILABLE_BACKENDS
    
    def get_backend_names(self) -> List[str]:
        """Get list of available backend names.
        
        Returns:
            Sorted list of backend names that can be used with the create command.
        """
        return list(self._backends.keys())
    
    def get_backend_class(self, name: str) -> Type[BaseBackend]:
        """Get backend class by name.
        
        Args:
            name: Name of the backend (e.g., 'database', 'api', 'filesystem').
        
        Returns:
            Backend class that can be instantiated for project generation.
        
        Raises:
            ValueError: If the backend name is not registered.
        """
        if name not in self._backends:
            raise ValueError(f"Unknown backend: {name}")
        return self._backends[name]
    
    def is_valid_backend(self, name: str) -> bool:
        """Check if backend name is valid.
        
        Args:
            name: Backend name to validate.
        
        Returns:
            True if the backend is registered, False otherwise.
        """
        return name in self._backends
    
    def get_all_backends(self) -> Dict[str, Type[BaseBackend]]:
        """Get all available backends.
        
        Returns:
            Dictionary mapping backend names to their implementation classes.
            This is a copy to prevent external modification.
        """
        return self._backends.copy()
    
    def register_backend(self, name: str, backend_class: Type[BaseBackend]) -> None:
        """Register a new backend.
        
        Args:
            name: Unique name for the backend.
            backend_class: Backend implementation class that inherits from BaseBackend.
        
        Raises:
            ValueError: If backend_class doesn't inherit from BaseBackend.
        """
        if not issubclass(backend_class, BaseBackend):
            raise ValueError("Backend must inherit from BaseBackend")
        self._backends[name] = backend_class
    
    def unregister_backend(self, name: str) -> None:
        """Unregister a backend.
        
        Args:
            name: Name of the backend to remove. If the backend doesn't exist,
                 this method does nothing (no error is raised).
        """
        if name in self._backends:
            del self._backends[name]


# Global instance
backend_registry = BackendRegistry()