"""Security utilities for ModelCtx."""

import re
import json
import ipaddress
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Union

from modelctx.exceptions import ValidationError


def sanitize_for_template(value: Any) -> str:
    """Safely sanitize value for template rendering.
    
    Args:
        value: Value to sanitize for template use.
    
    Returns:
        JSON-encoded string safe for template rendering, without HTML escaping.
    """
    try:
        # Use ensure_ascii=False to avoid unnecessary escaping in JSON
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Cannot safely serialize value for template: {e}")


def validate_sql_identifier(identifier: str) -> bool:
    """Validate SQL identifier to prevent injection.
    
    Args:
        identifier: SQL identifier (table name, column name, etc.)
    
    Returns:
        True if identifier is safe, False otherwise.
    """
    if not identifier:
        return False
    
    # Only allow alphanumeric and underscore, must start with letter or underscore
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if not re.match(pattern, identifier):
        return False
    
    # Check against SQL reserved words (basic list)
    reserved_words = {
        'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter',
        'table', 'database', 'index', 'view', 'procedure', 'function',
        'trigger', 'union', 'order', 'group', 'having', 'where', 'join'
    }
    
    if identifier.lower() in reserved_words:
        return False
    
    return True


def validate_file_path(file_path: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
    """Securely validate and resolve file path.
    
    Args:
        file_path: File path to validate.
        base_dir: Base directory that path must be within (if specified).
    
    Returns:
        Resolved and validated Path object.
    
    Raises:
        ValidationError: If path is invalid or unsafe.
    """
    try:
        path_obj = Path(file_path).resolve()
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    # Check for symlinks in the path components
    current = path_obj
    while current != current.parent:
        if current.is_symlink():
            raise ValidationError("Symlinks are not allowed in file paths")
        current = current.parent
    
    # Validate against base directory if specified
    if base_dir:
        base_dir_resolved = Path(base_dir).resolve()
        try:
            path_obj.relative_to(base_dir_resolved)
        except ValueError:
            raise ValidationError(f"Path {file_path} is outside allowed directory {base_dir}")
    
    return path_obj


def validate_url_safe(url: str) -> bool:
    """Validate URL for safety (prevent SSRF attacks).
    
    Args:
        url: URL to validate.
    
    Returns:
        True if URL is safe, False otherwise.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    
    # Only allow HTTP/HTTPS
    if parsed.scheme not in ('http', 'https'):
        return False
    
    # Check if hostname is an IP address
    if parsed.hostname:
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            # Block private networks, loopback, multicast
            if ip.is_private or ip.is_loopback or ip.is_multicast:
                return False
            # Block IPv4 link-local
            if isinstance(ip, ipaddress.IPv4Address) and ip.is_link_local:
                return False
            # Block IPv6 link-local and site-local
            if isinstance(ip, ipaddress.IPv6Address) and (ip.is_link_local or ip.is_site_local):
                return False
        except ValueError:
            # Not an IP address, which is OK for domain names
            pass
        
        # Additional domain name validation
        if parsed.hostname in ('localhost', '127.0.0.1', '::1'):
            return False
    
    return True


def sanitize_project_name(name: str) -> str:
    """Sanitize project name for safe use in file systems and code.
    
    Args:
        name: Project name to sanitize.
    
    Returns:
        Sanitized project name.
    
    Raises:
        ValidationError: If name cannot be safely sanitized.
    """
    if not name:
        raise ValidationError("Project name cannot be empty")
    
    # Remove any non-alphanumeric characters except hyphens and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    
    # Ensure it starts and ends with alphanumeric
    sanitized = re.sub(r'^[_-]+|[_-]+$', '', sanitized)
    
    if not sanitized:
        raise ValidationError("Project name must contain alphanumeric characters")
    
    if len(sanitized) > 50:
        raise ValidationError("Project name too long (max 50 characters)")
    
    # Check against reserved names
    reserved_names = {
        'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5',
        'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4',
        'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9', 'test', 'tmp', 'temp'
    }
    
    if sanitized.lower() in reserved_names:
        raise ValidationError(f"'{sanitized}' is a reserved name and cannot be used")
    
    return sanitized


def escape_shell_argument(arg: str) -> str:
    """Escape shell argument to prevent injection.
    
    Args:
        arg: Argument to escape.
    
    Returns:
        Shell-escaped argument.
    """
    # Simple approach: only allow alphanumeric, hyphens, underscores, dots, slashes
    if re.match(r'^[a-zA-Z0-9._/-]+$', arg):
        return arg
    
    # For anything else, use single quotes and escape single quotes
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def validate_backend_parameters(params: Dict[str, Any], backend_type: str) -> Dict[str, Any]:
    """Validate and sanitize backend parameters.
    
    Args:
        params: Parameters to validate.
        backend_type: Type of backend for context-specific validation.
    
    Returns:
        Validated and sanitized parameters.
    
    Raises:
        ValidationError: If parameters are invalid or unsafe.
    """
    validated = {}
    
    for key, value in params.items():
        # Validate parameter name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            raise ValidationError(f"Invalid parameter name: {key}")
        
        # Type-specific validation
        if backend_type == 'database':
            if key == 'database_url' and isinstance(value, str):
                # Basic database URL validation
                if not re.match(r'^(postgresql|mysql|sqlite):\/\/', value):
                    raise ValidationError("Invalid database URL scheme")
        
        elif backend_type == 'api':
            if key == 'base_url' and isinstance(value, str):
                if not validate_url_safe(value):
                    raise ValidationError(f"Unsafe URL: {value}")
        
        elif backend_type == 'filesystem':
            if key in ('base_path', 'allowed_paths') and isinstance(value, str):
                validate_file_path(value)
        
        validated[key] = value
    
    return validated