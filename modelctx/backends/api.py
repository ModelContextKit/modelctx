"""REST API backend implementation for MCP servers."""

from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class APIBackend(BaseBackend):
    """Backend for connecting to REST APIs with authentication and rate limiting."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "api"
    
    @classmethod
    def get_description(cls) -> str:
        return "Connect to REST APIs with authentication, rate limiting, and error handling"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "httpx>=0.24.0",
            "aiohttp>=3.8.0",
            "pydantic>=2.0.0",
            "python-jose[cryptography]>=3.3.0",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "api_request",
                "description": "Make HTTP request to configured API with authentication and rate limiting",
                "parameters": "endpoint: str, method: str = 'GET', data: dict = None, params: dict = None, headers: dict = None",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint to call"
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method to use",
                            "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                            "default": "GET"
                        },
                        "data": {
                            "type": "object",
                            "description": "Request body data",
                            "additionalProperties": True
                        },
                        "params": {
                            "type": "object",
                            "description": "Query parameters",
                            "additionalProperties": True
                        },
                        "headers": {
                            "type": "object",
                            "description": "Additional request headers",
                            "additionalProperties": True
                        }
                    },
                    "required": ["endpoint"]
                },
                "implementation": '''
endpoint = arguments.get("endpoint", "")
method = arguments.get("method", "GET")
data = arguments.get("data")
params = arguments.get("params")
headers = arguments.get("headers")

logger.info(f"Making {method} request to {endpoint}")

# Validate endpoint
if not _validate_endpoint(endpoint):
    raise ValueError(f"Invalid endpoint: {endpoint}")

# Check rate limiting
if not await _check_rate_limit():
    raise ValueError("Rate limit exceeded. Please wait before making more requests.")

# Prepare URL
url = _build_url(endpoint)

# Prepare headers with authentication
request_headers = await _prepare_headers(headers or {})

# Prepare request data
request_data = data or {}
request_params = params or {}

# Make request using httpx client
async with get_http_client() as client:
    response = await client.request(
        method=method.upper(),
        url=url,
        json=request_data if method.upper() in ['POST', 'PUT', 'PATCH'] and request_data else None,
        params=request_params,
        headers=request_headers,
        timeout=REQUEST_TIMEOUT
    )
    
    # Log request details (without sensitive data)
    await _log_request(method, url, response.status_code)
    
    # Handle response
    if response.status_code >= 400:
        error_detail = await _extract_error_detail(response)
        error_data = {
            "success": False,
            "status_code": response.status_code,
            "error": f"HTTP {response.status_code}: {error_detail}",
            "headers": dict(response.headers)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]
    
    # Parse response
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            response_data = response.json()
        else:
            response_data = response.text
    except Exception as parse_error:
        response_data = response.text
        logger.warning(f"Failed to parse JSON response: {parse_error}")
    
    result_data = {
        "success": True,
        "status_code": response.status_code,
        "data": response_data,
        "headers": dict(response.headers),
        "url": str(response.url)
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]'''
            },
            {
                "name": "get_api_status",
                "description": "Check API health and connectivity",
                "parameters": "",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "implementation": '''
logger.info("Checking API status")

# Use health check endpoint if configured
health_endpoint = get_health_endpoint()

async with get_http_client() as client:
    start_time = time.time()
    
    response = await client.get(
        health_endpoint,
        headers=await _prepare_headers({}),
        timeout=10  # Shorter timeout for health checks
    )
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    result_data = {
        "success": True,
        "status": "healthy" if response.status_code < 400 else "unhealthy",
        "status_code": response.status_code,
        "response_time_ms": round(response_time, 2),
        "api_url": BASE_URL,
        "timestamp": datetime.now().isoformat(),
        "rate_limit_remaining": await _get_rate_limit_remaining()
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]'''
            },
            {
                "name": "list_endpoints",
                "description": "List available API endpoints (if API supports discovery)",
                "parameters": "",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "implementation": '''
logger.info("Discovering API endpoints")

# Try common discovery endpoints
discovery_endpoints = [
    "/", "/api", "/swagger.json", "/openapi.json", 
    "/docs", "/api/docs", "/.well-known/endpoints"
]

discovered_endpoints = []

async with get_http_client() as client:
    for endpoint in discovery_endpoints:
        try:
            response = await client.get(
                _build_url(endpoint),
                headers=await _prepare_headers({}),
                timeout=5
            )
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    data = response.json()
                    
                    # Extract endpoints from OpenAPI/Swagger
                    if "paths" in data:
                        for path, methods in data["paths"].items():
                            for method, details in methods.items():
                                discovered_endpoints.append({
                                    "path": path,
                                    "method": method.upper(),
                                    "summary": details.get("summary", ""),
                                    "description": details.get("description", "")
                                })
                
                discovered_endpoints.append({
                    "path": endpoint,
                    "method": "GET",
                    "status": "available",
                    "content_type": content_type
                })
                
        except Exception:
            continue

result_data = {
    "success": True,
    "endpoints": discovered_endpoints,
    "discovery_attempted": len(discovery_endpoints),
    "base_url": BASE_URL
}

return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]'''
            },
            {
                "name": "validate_auth",
                "description": "Validate API authentication and permissions",
                "parameters": "",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "implementation": '''
logger.info("Validating API authentication")

# Try to access a protected endpoint or user info
auth_test_endpoints = [
    "/user", "/me", "/auth/verify", "/api/user", 
    "/account", "/profile", "/whoami"
]

auth_results = []

async with get_http_client() as client:
    for endpoint in auth_test_endpoints:
        try:
            response = await client.get(
                _build_url(endpoint),
                headers=await _prepare_headers({}),
                timeout=10
            )
            
            auth_results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "authenticated": response.status_code not in [401, 403],
                "response_size": len(response.content)
            })
            
            # If we get a successful response, try to extract user info
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "authenticated": True,
                            "endpoint": endpoint,
                            "user_info": user_data,
                            "auth_type": AUTH_TYPE
                        }, indent=2)
                    )]
                except:
                    pass
                    
        except Exception as test_error:
            auth_results.append({
                "endpoint": endpoint,
                "error": str(test_error)
            })

# Analyze results
authenticated_endpoints = [r for r in auth_results if r.get("authenticated", False)]

result_data = {
    "success": len(authenticated_endpoints) > 0,
    "authenticated": len(authenticated_endpoints) > 0,
    "auth_type": AUTH_TYPE,
    "test_results": auth_results,
    "working_endpoints": len(authenticated_endpoints)
}

return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_api_info",
                "uri": "api://info",
                "description": "API configuration and status information",
                "parameters": "",
                "implementation": '''
# Get current API configuration (without sensitive data)
api_info = {
    "base_url": BASE_URL,
    "auth_type": AUTH_TYPE,
    "rate_limit": {
        "requests_per_minute": RATE_LIMIT_PER_MINUTE,
        "remaining": await _get_rate_limit_remaining()
    },
    "timeout": REQUEST_TIMEOUT,
    "configured_endpoints": len(ALLOWED_ENDPOINTS) if ALLOWED_ENDPOINTS else "unrestricted",
    "last_health_check": await _get_last_health_check()
}

return json.dumps(api_info, indent=2)
'''
            },
            {
                "name": "get_rate_limit_status",
                "uri": "api://rate-limit",
                "description": "Current rate limiting status and usage",
                "parameters": "",
                "implementation": '''
rate_limit_info = {
    "requests_per_minute": RATE_LIMIT_PER_MINUTE,
    "current_usage": await _get_current_usage(),
    "remaining": await _get_rate_limit_remaining(),
    "reset_time": await _get_rate_limit_reset_time(),
    "window_start": await _get_rate_limit_window_start()
}

return json.dumps(rate_limit_info, indent=2)
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "import time",
            "import asyncio",
            "from datetime import datetime, timedelta",
            "from contextlib import asynccontextmanager",
            "from typing import Optional, Dict, Any",
            "import httpx",
            "import os",
            "import re",
            "from urllib.parse import urljoin, urlparse",
            "import hashlib",
            "import base64",
        ]
    
    def get_init_code(self) -> str:
        base_url = self.config.parameters.get("base_url", "")
        auth_type = self.config.parameters.get("auth_type", "none")
        rate_limit = self.config.parameters.get("rate_limit_requests_per_minute", 60)
        timeout = self.config.parameters.get("request_timeout", 30)
        
        return f'''
# API Configuration
BASE_URL = os.getenv("API_BASE_URL", "{base_url}")
AUTH_TYPE = os.getenv("API_AUTH_TYPE", "{auth_type}")
API_KEY = os.getenv("API_KEY", "")
API_TOKEN = os.getenv("API_TOKEN", "")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")

# Rate limiting and timeouts
RATE_LIMIT_PER_MINUTE = {rate_limit}
REQUEST_TIMEOUT = {timeout}
ALLOWED_ENDPOINTS = os.getenv("ALLOWED_ENDPOINTS", "").split(",") if os.getenv("ALLOWED_ENDPOINTS") else []

# Project configuration
PROJECT_NAME = "{self.config.project_name}"

# Rate limiting storage (in-memory for now)
rate_limit_tracker = {{}}
request_history = []

@asynccontextmanager
async def get_http_client():
    """Get HTTP client with proper configuration."""
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(REQUEST_TIMEOUT),
        follow_redirects=True,
        verify=True  # SSL verification
    ) as client:
        yield client

def _build_url(endpoint: str) -> str:
    """Build full URL from base URL and endpoint."""
    if endpoint.startswith(("http://", "https://")):
        return endpoint
    
    # Remove leading slash if present
    endpoint = endpoint.lstrip("/")
    
    # Join with base URL
    return urljoin(BASE_URL.rstrip("/") + "/", endpoint)

def _validate_endpoint(endpoint: str) -> bool:
    """Validate endpoint against allowed endpoints list."""
    if not ALLOWED_ENDPOINTS:
        return True  # No restrictions
    
    # Normalize endpoint
    normalized = endpoint.lstrip("/")
    
    # Check against allowed patterns
    for allowed in ALLOWED_ENDPOINTS:
        allowed = allowed.strip()
        if not allowed:
            continue
        
        # Support wildcards
        if allowed.endswith("*"):
            if normalized.startswith(allowed[:-1]):
                return True
        elif normalized == allowed or endpoint == allowed:
            return True
    
    return False

async def _prepare_headers(additional_headers: Dict[str, str]) -> Dict[str, str]:
    """Prepare request headers with authentication."""
    headers = {{
        "User-Agent": f"{{PROJECT_NAME}}/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        **additional_headers
    }}
    
    # Add authentication headers based on type
    if AUTH_TYPE == "bearer" and BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {{BEARER_TOKEN}}"
    elif AUTH_TYPE == "api_key" and API_KEY:
        headers["X-API-Key"] = API_KEY
        # Some APIs use different header names
        headers["Authorization"] = f"Bearer {{API_KEY}}"
    elif AUTH_TYPE == "token" and API_TOKEN:
        headers["Authorization"] = f"Token {{API_TOKEN}}"
    elif AUTH_TYPE == "oauth2":
        # OAuth2 would require more complex implementation
        access_token = await _get_oauth_access_token()
        if access_token:
            headers["Authorization"] = f"Bearer {{access_token}}"
    
    return headers

async def _check_rate_limit() -> bool:
    """Check if request is within rate limits."""
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Clean old requests
    global request_history
    request_history = [req_time for req_time in request_history if req_time > minute_ago]
    
    # Check if we're under the limit
    if len(request_history) >= RATE_LIMIT_PER_MINUTE:
        return False
    
    # Record this request
    request_history.append(current_time)
    return True

async def _get_rate_limit_remaining() -> int:
    """Get remaining requests in current rate limit window."""
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Count requests in last minute
    recent_requests = [req_time for req_time in request_history if req_time > minute_ago]
    return max(0, RATE_LIMIT_PER_MINUTE - len(recent_requests))

async def _get_current_usage() -> int:
    """Get current usage in rate limit window."""
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Count requests in last minute
    recent_requests = [req_time for req_time in request_history if req_time > minute_ago]
    return len(recent_requests)

async def _get_rate_limit_reset_time() -> str:
    """Get time when rate limit window resets."""
    if not request_history:
        return datetime.now().isoformat()
    
    oldest_request = min(request_history)
    reset_time = datetime.fromtimestamp(oldest_request + 60)
    return reset_time.isoformat()

async def _get_rate_limit_window_start() -> str:
    """Get start time of current rate limit window."""
    current_time = time.time()
    window_start = datetime.fromtimestamp(current_time - 60)
    return window_start.isoformat()

async def _log_request(method: str, url: str, status_code: int) -> None:
    """Log request details (without sensitive information)."""
    # Parse URL to remove query parameters that might contain sensitive data
    parsed = urlparse(url)
    safe_url = f"{{parsed.scheme}}://{{parsed.netloc}}{{parsed.path}}"
    
    logger.info(f"{{method}} {{safe_url}} -> {{status_code}}")

async def _extract_error_detail(response) -> str:
    """Extract error details from response."""
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            error_data = response.json()
            
            # Try common error message fields
            for field in ["message", "error", "detail", "error_description"]:
                if field in error_data:
                    return str(error_data[field])
            
            # Return first string value found
            for value in error_data.values():
                if isinstance(value, str):
                    return value
        
        # Fallback to response text
        return response.text or response.reason_phrase or "Unknown error"
        
    except Exception:
        return response.reason_phrase or "Unknown error"

def get_health_endpoint() -> str:
    """Get health check endpoint URL."""
    health_endpoints = ["/health", "/status", "/ping", "/api/health", "/"]
    
    # Use configured health endpoint or default
    configured_health = os.getenv("API_HEALTH_ENDPOINT", health_endpoints[0])
    return _build_url(configured_health)

async def _get_last_health_check() -> Optional[str]:
    """Get timestamp of last health check."""
    # In a real implementation, this would be stored persistently
    return datetime.now().isoformat()

async def _get_oauth_access_token() -> Optional[str]:
    """Get OAuth2 access token (simplified implementation)."""
    # This is a placeholder - real OAuth2 implementation would be more complex
    if OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET:
        # Would implement OAuth2 client credentials flow here
        pass
    return None

'''
    
    def get_cleanup_code(self) -> str:
        return '''# Cleanup any remaining HTTP connections
        logger.info("Cleaning up HTTP connections...")'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Check required parameters
        base_url = self.config.parameters.get("base_url")
        if not base_url:
            errors.append("base_url is required")
        else:
            # Basic URL validation
            if not base_url.startswith(("http://", "https://")):
                errors.append("base_url must be a valid HTTP/HTTPS URL")
        
        # Validate auth type
        auth_type = self.config.parameters.get("auth_type", "none")
        valid_auth_types = ["none", "bearer", "api_key", "token", "oauth2"]
        if auth_type not in valid_auth_types:
            errors.append(f"auth_type must be one of: {', '.join(valid_auth_types)}")
        
        # Check auth credentials based on type
        if auth_type != "none":
            if auth_type == "bearer" and not self.config.parameters.get("bearer_token"):
                errors.append("bearer_token is required when auth_type is 'bearer'")
            elif auth_type == "api_key" and not self.config.parameters.get("api_key"):
                errors.append("api_key is required when auth_type is 'api_key'")
            elif auth_type == "token" and not self.config.parameters.get("api_token"):
                errors.append("api_token is required when auth_type is 'token'")
            elif auth_type == "oauth2":
                if not self.config.parameters.get("oauth_client_id"):
                    errors.append("oauth_client_id is required when auth_type is 'oauth2'")
                if not self.config.parameters.get("oauth_client_secret"):
                    errors.append("oauth_client_secret is required when auth_type is 'oauth2'")
        
        # Validate rate limit
        rate_limit = self.config.parameters.get("rate_limit_requests_per_minute", 60)
        if not isinstance(rate_limit, int) or rate_limit < 1 or rate_limit > 10000:
            errors.append("rate_limit_requests_per_minute must be an integer between 1 and 10000")
        
        # Validate timeout
        timeout = self.config.parameters.get("request_timeout", 30)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            errors.append("request_timeout must be an integer between 1 and 300 seconds")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "API_BASE_URL": "Base URL for the API (e.g., https://api.example.com)",
            "API_AUTH_TYPE": "Authentication type: none, bearer, api_key, token, oauth2",
            "API_KEY": "API key for api_key authentication",
            "API_TOKEN": "API token for token authentication",
            "BEARER_TOKEN": "Bearer token for bearer authentication",
            "OAUTH_CLIENT_ID": "OAuth2 client ID",
            "OAUTH_CLIENT_SECRET": "OAuth2 client secret",
            "ALLOWED_ENDPOINTS": "Comma-separated list of allowed endpoints (optional)",
            "API_HEALTH_ENDPOINT": "Health check endpoint (optional, default: /health)",
        }
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text",
                "message": "Enter a description for your API MCP server:",
                "default": "MCP server with REST API backend",
            },
            {
                "name": "base_url",
                "type": "text",
                "message": "Enter the base URL of the API:",
                "default": "https://api.example.com",
                "required": True,
                "validator": "url",
            },
            {
                "name": "auth_type",
                "type": "choice",
                "message": "Select authentication type:",
                "choices": ["none", "bearer", "api_key", "token", "oauth2"],
                "default": "bearer",
                "required": True,
            },
            {
                "name": "api_key",
                "type": "text",
                "message": "Enter API key (leave empty if not using api_key auth):",
                "default": "",
            },
            {
                "name": "bearer_token",
                "type": "text",
                "message": "Enter Bearer token (leave empty if not using bearer auth):",
                "default": "",
            },
            {
                "name": "rate_limit_requests_per_minute",
                "type": "int",
                "message": "Enter rate limit (requests per minute):",
                "default": 60,
            },
            {
                "name": "request_timeout",
                "type": "int",
                "message": "Enter request timeout (seconds):",
                "default": 30,
            },
            {
                "name": "allowed_endpoints",
                "type": "text",
                "message": "Enter allowed endpoints (comma-separated, * for wildcard, empty for all):",
                "default": "",
            },
        ]