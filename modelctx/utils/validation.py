"""Validation utilities for MCP setup tool."""

import re
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional, Union, Dict, Any


def validate_project_name(name: str) -> bool:
    """
    Validate project name.
    
    Rules:
    - Only alphanumeric characters, hyphens, and underscores
    - Cannot start or end with hyphens or underscores
    - Length between 1 and 50 characters
    """
    if not name or len(name) > 50:
        return False
    
    # Check pattern
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
    return bool(re.match(pattern, name))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_file_path(path: str) -> bool:
    """
    Validate file path.
    
    Args:
        path: File path to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    if not path:
        return False
    
    try:
        Path(path)
        return True
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_port(port: Union[str, int]) -> bool:
    """
    Validate port number.
    
    Args:
        port: Port number to validate (as string or int)
        
    Returns:
        True if port is valid, False otherwise
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def validate_database_url(url: str) -> bool:
    """
    Validate database URL format.
    
    Args:
        url: Database URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Common database URL patterns
    patterns = [
        r'^postgresql://[^:]+:[^@]+@[^:/]+:\d+/\w+$',  # PostgreSQL
        r'^mysql://[^:]+:[^@]+@[^:/]+:\d+/\w+$',       # MySQL
        r'^sqlite:///[^?]+\.db$',                      # SQLite
        r'^mongodb://[^:]+:[^@]+@[^:/]+:\d+/\w+$',     # MongoDB
    ]
    
    return any(re.match(pattern, url) for pattern in patterns)


def validate_json_string(json_str: str) -> bool:
    """
    Validate JSON string format.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if JSON is valid, False otherwise
    """
    if not json_str:
        return False
    
    try:
        import json
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed'
    
    return sanitized


def validate_environment_variable_name(name: str) -> bool:
    """
    Validate environment variable name.
    
    Args:
        name: Environment variable name
        
    Returns:
        True if name is valid, False otherwise
    """
    if not name:
        return False
    
    # Environment variable names should be uppercase with underscores
    pattern = r'^[A-Z][A-Z0-9_]*$'
    return bool(re.match(pattern, name))


def validate_python_identifier(identifier: str) -> bool:
    """
    Validate Python identifier (variable, function, class name).
    
    Args:
        identifier: Python identifier to validate
        
    Returns:
        True if identifier is valid, False otherwise
    """
    if not identifier:
        return False
    
    return identifier.isidentifier() and not identifier.iskeyword()


def check_path_traversal(path: str, base_path: str) -> bool:
    """
    Check if a path contains path traversal attempts.
    
    Args:
        path: Path to check
        base_path: Base path that should contain the resolved path
        
    Returns:
        True if path is safe, False if it contains traversal
    """
    try:
        # Resolve both paths
        resolved_path = Path(base_path).resolve() / Path(path)
        resolved_base = Path(base_path).resolve()
        
        # Check if resolved path is within base path
        return str(resolved_path).startswith(str(resolved_base))
    except Exception:
        return False


def validate_api_key_format(api_key: str, key_type: str = "generic") -> bool:
    """
    Validate API key format based on type.
    
    Args:
        api_key: API key to validate
        key_type: Type of API key (generic, jwt, uuid, etc.)
        
    Returns:
        True if API key format is valid, False otherwise
    """
    if not api_key:
        return False
    
    if key_type == "jwt":
        # JWT tokens have 3 parts separated by dots
        parts = api_key.split('.')
        return len(parts) == 3 and all(len(part) > 0 for part in parts)
    elif key_type == "uuid":
        # UUID format
        pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        return bool(re.match(pattern, api_key))
    elif key_type == "bearer":
        # Bearer token (usually starts with specific prefix)
        return len(api_key) >= 20 and not api_key.isspace()
    else:
        # Generic API key - at least 10 characters, alphanumeric
        return len(api_key) >= 10 and re.match(r'^[a-zA-Z0-9_-]+$', api_key)


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address (IPv4 or IPv6).
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if IP is valid, False otherwise
    """
    if not ip:
        return False
    
    import socket
    
    # Try IPv4
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        pass
    
    # Try IPv6
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        pass
    
    return False


def get_validation_errors(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate data against a simple schema and return errors.
    
    Args:
        data: Data to validate
        schema: Validation schema
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for field, rules in schema.items():
        value = data.get(field)
        field_errors = validate_field(field, value, rules)
        errors.extend(field_errors)
    
    return errors


def validate_field(field_name: str, value: Any, rules: Dict[str, Any]) -> List[str]:
    """
    Validate a single field against rules.
    
    Args:
        field_name: Name of the field
        value: Value to validate
        rules: Validation rules
        
    Returns:
        List of error messages for this field
    """
    errors = []
    
    # Required check
    if rules.get("required", False) and (value is None or value == ""):
        errors.append(f"{field_name} is required")
        return errors  # Don't continue if required field is missing
    
    # Skip other validations if value is empty and not required
    if value is None or value == "":
        return errors
    
    # Type check
    expected_type = rules.get("type")
    if expected_type and not isinstance(value, expected_type):
        errors.append(f"{field_name} must be of type {expected_type.__name__}")
    
    # String validations
    if isinstance(value, str):
        min_length = rules.get("min_length")
        if min_length and len(value) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters")
        
        max_length = rules.get("max_length")
        if max_length and len(value) > max_length:
            errors.append(f"{field_name} must be at most {max_length} characters")
        
        pattern = rules.get("pattern")
        if pattern and not re.match(pattern, value):
            errors.append(f"{field_name} format is invalid")
        
        # Special format validations
        format_type = rules.get("format")
        if format_type == "email" and not validate_email(value):
            errors.append(f"{field_name} must be a valid email address")
        elif format_type == "url" and not validate_url(value):
            errors.append(f"{field_name} must be a valid URL")
    
    # Numeric validations
    if isinstance(value, (int, float)):
        minimum = rules.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{field_name} must be at least {minimum}")
        
        maximum = rules.get("maximum")
        if maximum is not None and value > maximum:
            errors.append(f"{field_name} must be at most {maximum}")
    
    # Choice validation
    choices = rules.get("choices")
    if choices and value not in choices:
        errors.append(f"{field_name} must be one of: {', '.join(map(str, choices))}")
    
    return errors