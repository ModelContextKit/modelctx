"""Filesystem backend implementation for MCP servers."""

import os
from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class FilesystemBackend(BaseBackend):
    """Backend for safe filesystem operations with access controls."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "filesystem"
    
    @classmethod
    def get_description(cls) -> str:
        return "Access and manipulate local files and directories with security controls"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "aiofiles>=23.0.0",
            "watchdog>=3.0.0",
            "pathspec>=0.11.0",
            "magic>=0.4.27",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "read_file",
                "description": "Read contents of a file with security checks",
                "parameters": "file_path: str, encoding: str = 'utf-8', max_size: int = None",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Maximum file size in bytes"
                        }
                    },
                    "required": ["file_path"]
                },
                "implementation": '''
file_path = arguments.get("file_path", "")
encoding = arguments.get("encoding", "utf-8")
max_size = arguments.get("max_size")

logger.info(f"Reading file: {file_path}")

# Validate and resolve file path
safe_path = await _validate_and_resolve_path(file_path)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {file_path}",
        "path": file_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check if file exists and is a file
if not safe_path.exists():
    result_data = {
        "success": False,
        "error": f"File not found: {file_path}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

if not safe_path.is_file():
    result_data = {
        "success": False,
        "error": f"Path is not a file: {file_path}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check file size
file_size = safe_path.stat().st_size
max_file_size = max_size or MAX_FILE_SIZE

if file_size > max_file_size:
    result_data = {
        "success": False,
        "error": f"File too large: {file_size} bytes (max: {max_file_size})",
        "size": file_size,
        "max_size": max_file_size
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check file type
if not await _is_allowed_file_type(safe_path):
    result_data = {
        "success": False,
        "error": f"File type not allowed: {safe_path.suffix}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Read file content
try:
    async with aiofiles.open(safe_path, 'r', encoding=encoding) as f:
        content = await f.read()
except UnicodeDecodeError:
    # Try binary read for non-text files
    async with aiofiles.open(safe_path, 'rb') as f:
        binary_content = await f.read()
        content = base64.b64encode(binary_content).decode('utf-8')
        encoding = 'base64'

result_data = {
    "success": True,
    "content": content,
    "encoding": encoding,
    "size": file_size,
    "path": str(safe_path),
    "modified": safe_path.stat().st_mtime,
    "mime_type": await _get_mime_type(safe_path)
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            },
            {
                "name": "write_file",
                "description": "Write content to a file with security checks",
                "parameters": "file_path: str, content: str, encoding: str = 'utf-8', create_dirs: bool = False",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "Create parent directories if they don't exist",
                            "default": False
                        }
                    },
                    "required": ["file_path", "content"]
                },
                "implementation": '''
file_path = arguments.get("file_path", "")
content = arguments.get("content", "")
encoding = arguments.get("encoding", "utf-8")
create_dirs = arguments.get("create_dirs", False)

logger.info(f"Writing file: {file_path}")

# Check if filesystem is read-only
if READ_ONLY_MODE:
    result_data = {
        "success": False,
        "error": "Filesystem is in read-only mode",
        "path": file_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Validate and resolve file path
safe_path = await _validate_and_resolve_path(file_path, allow_create=True)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {file_path}",
        "path": file_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check if we can write to parent directory
parent_dir = safe_path.parent
if not parent_dir.exists() and not create_dirs:
    result_data = {
        "success": False,
        "error": f"Parent directory does not exist: {parent_dir}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Create parent directories if requested
if create_dirs and not parent_dir.exists():
    parent_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created parent directories: {parent_dir}")

# Check file extension
if not await _is_allowed_file_type(safe_path):
    result_data = {
        "success": False,
        "error": f"File type not allowed: {safe_path.suffix}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check content size
content_size = len(content.encode(encoding))
if content_size > MAX_FILE_SIZE:
    result_data = {
        "success": False,
        "error": f"Content too large: {content_size} bytes (max: {MAX_FILE_SIZE})",
        "size": content_size,
        "max_size": MAX_FILE_SIZE
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Handle different encodings
if encoding == 'base64':
    # Decode base64 content and write as binary
    try:
        binary_content = base64.b64decode(content)
        async with aiofiles.open(safe_path, 'wb') as f:
            await f.write(binary_content)
    except Exception as e:
        raise ValueError(f"Invalid base64 content: {e}")
else:
    # Write as text
    async with aiofiles.open(safe_path, 'w', encoding=encoding) as f:
        await f.write(content)

# Get file stats
file_stats = safe_path.stat()

result_data = {
    "success": True,
    "path": str(safe_path),
    "size": file_stats.st_size,
    "created": not safe_path.existed_before if hasattr(safe_path, 'existed_before') else "unknown",
    "encoding": encoding,
    "modified": file_stats.st_mtime
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory with metadata",
                "parameters": "dir_path: str, include_hidden: bool = False, recursive: bool = False, max_depth: int = 3",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "Path to the directory to list"
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List directory contents recursively",
                            "default": False
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum depth for recursive listing",
                            "default": 3
                        }
                    },
                    "required": ["dir_path"]
                },
                "implementation": '''
dir_path = arguments.get("dir_path", "")
include_hidden = arguments.get("include_hidden", False)
recursive = arguments.get("recursive", False)
max_depth = arguments.get("max_depth", 3)

logger.info(f"Listing directory: {dir_path}")

# Validate and resolve directory path
safe_path = await _validate_and_resolve_path(dir_path)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {dir_path}",
        "path": dir_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check if path exists and is a directory
if not safe_path.exists():
    result_data = {
        "success": False,
        "error": f"Directory not found: {dir_path}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

if not safe_path.is_dir():
    result_data = {
        "success": False,
        "error": f"Path is not a directory: {dir_path}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# List directory contents
items = []

if recursive:
    # Recursive listing with depth limit
    items = await _list_directory_recursive(safe_path, include_hidden, max_depth)
else:
    # Simple listing
    for item in safe_path.iterdir():
        # Skip hidden files if not requested
        if not include_hidden and item.name.startswith('.'):
            continue
        
        item_info = await _get_item_info(item)
        items.append(item_info)

# Sort items by type (directories first) then by name
items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))

result_data = {
    "success": True,
    "path": str(safe_path),
    "items": items,
    "count": len(items),
    "recursive": recursive,
    "include_hidden": include_hidden
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            },
            {
                "name": "search_files",
                "description": "Search for files by name pattern and content",
                "parameters": "directory: str, pattern: str, search_content: bool = False, max_results: int = 100",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory to search in"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (glob or regex)"
                        },
                        "search_content": {
                            "type": "boolean",
                            "description": "Search file contents in addition to names",
                            "default": False
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 100
                        }
                    },
                    "required": ["directory", "pattern"]
                },
                "implementation": '''
directory = arguments.get("directory", "")
pattern = arguments.get("pattern", "")
search_content = arguments.get("search_content", False)
max_results = arguments.get("max_results", 100)

logger.info(f"Searching files in {directory} with pattern: {pattern}")

# Validate and resolve directory path
safe_path = await _validate_and_resolve_path(directory)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {directory}",
        "path": directory
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

if not safe_path.exists() or not safe_path.is_dir():
    result_data = {
        "success": False,
        "error": f"Invalid directory: {directory}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Compile pattern for filename matching
import fnmatch
import re

# Support both glob patterns and regex
if pattern.startswith('/') and pattern.endswith('/'):
    # Regex pattern
    regex_pattern = re.compile(pattern[1:-1], re.IGNORECASE)
    def matches_pattern(name):
        return bool(regex_pattern.search(name))
else:
    # Glob pattern
    def matches_pattern(name):
        return fnmatch.fnmatch(name.lower(), pattern.lower())

results = []
searched_files = 0

# Search files recursively
for item in safe_path.rglob('*'):
    if len(results) >= max_results:
        break
        
    if item.is_file():
        searched_files += 1
        
        # Check filename pattern
        name_match = matches_pattern(item.name)
        content_match = False
        
        # Search content if requested and file type is allowed
        if search_content and await _is_text_file(item):
            try:
                if item.stat().st_size <= MAX_SEARCH_FILE_SIZE:
                    async with aiofiles.open(item, 'r', encoding='utf-8', errors='ignore') as f:
                        content = await f.read()
                        content_match = pattern.lower() in content.lower()
            except Exception:
                # Skip files that can't be read
                pass
        
        # Add to results if matches
        if name_match or content_match:
            item_info = await _get_item_info(item)
            item_info.update({
                "name_match": name_match,
                "content_match": content_match,
                "relative_path": str(item.relative_to(safe_path))
            })
            results.append(item_info)

result_data = {
    "success": True,
    "results": results,
    "pattern": pattern,
    "search_directory": str(safe_path),
    "total_matches": len(results),
    "files_searched": searched_files,
    "search_content": search_content,
    "max_results": max_results,
    "truncated": len(results) >= max_results
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            },
            {
                "name": "create_directory",
                "description": "Create a new directory with proper permissions",
                "parameters": "dir_path: str, parents: bool = True",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "Path to the directory to create"
                        },
                        "parents": {
                            "type": "boolean",
                            "description": "Create parent directories if they don't exist",
                            "default": True
                        }
                    },
                    "required": ["dir_path"]
                },
                "implementation": '''
dir_path = arguments.get("dir_path", "")
parents = arguments.get("parents", True)

logger.info(f"Creating directory: {dir_path}")

# Check if filesystem is read-only
if READ_ONLY_MODE:
    result_data = {
        "success": False,
        "error": "Filesystem is in read-only mode",
        "path": dir_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Validate and resolve directory path
safe_path = await _validate_and_resolve_path(dir_path, allow_create=True)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {dir_path}",
        "path": dir_path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check if directory already exists
if safe_path.exists():
    if safe_path.is_dir():
        result_data = {
            "success": True,
            "path": str(safe_path),
            "created": False,
            "message": "Directory already exists"
        }
        return [TextContent(
            type="text",
            text=json.dumps(result_data, indent=2)
        )]
    else:
        result_data = {
            "success": False,
            "error": f"Path exists but is not a directory: {dir_path}",
            "path": str(safe_path)
        }
        return [TextContent(
            type="text",
            text=json.dumps(result_data, indent=2)
        )]

# Create directory
safe_path.mkdir(parents=parents, exist_ok=True)

result_data = {
    "success": True,
    "path": str(safe_path),
    "created": True,
    "parents": parents
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            },
            {
                "name": "delete_file",
                "description": "Delete a file or directory with confirmation",
                "parameters": "path: str, recursive: bool = False, confirm: bool = True",
                "return_type": "list[TextContent]",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file or directory to delete"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Delete directories recursively",
                            "default": False
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Require confirmation for dangerous operations",
                            "default": True
                        }
                    },
                    "required": ["path"]
                },
                "implementation": '''
path = arguments.get("path", "")
recursive = arguments.get("recursive", False)
confirm = arguments.get("confirm", True)

logger.info(f"Deleting: {path}")

# Check if filesystem is read-only
if READ_ONLY_MODE:
    result_data = {
        "success": False,
        "error": "Filesystem is in read-only mode",
        "path": path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Validate and resolve path
safe_path = await _validate_and_resolve_path(path)
if not safe_path:
    result_data = {
        "success": False,
        "error": f"Access denied or invalid path: {path}",
        "path": path
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Check if path exists
if not safe_path.exists():
    result_data = {
        "success": False,
        "error": f"Path not found: {path}",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Safety check - require confirmation for dangerous operations
if confirm and not await _confirm_deletion(safe_path):
    result_data = {
        "success": False,
        "error": "Deletion not confirmed or path is protected",
        "path": str(safe_path)
    }
    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]

# Get info before deletion
was_directory = safe_path.is_dir()
file_count = 0

if was_directory:
    if recursive:
        # Count files for reporting
        file_count = sum(1 for _ in safe_path.rglob('*') if _.is_file())
        import shutil
        shutil.rmtree(safe_path)
    else:
        # Only delete if empty
        try:
            safe_path.rmdir()
        except OSError:
            result_data = {
                "success": False,
                "error": "Directory not empty (use recursive=True to force)",
                "path": str(safe_path)
            }
            return [TextContent(
                type="text",
                text=json.dumps(result_data, indent=2)
            )]
else:
    safe_path.unlink()
    file_count = 1

result_data = {
    "success": True,
    "path": str(safe_path),
    "was_directory": was_directory,
    "files_deleted": file_count,
    "recursive": recursive
}
return [TextContent(
    type="text",
    text=json.dumps(result_data, indent=2)
)]
'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_filesystem_info",
                "uri": "fs://info",
                "description": "Filesystem configuration and allowed paths",
                "parameters": "",
                "implementation": '''
filesystem_info = {
    "allowed_paths": [str(p) for p in ALLOWED_PATHS],
    "read_only_mode": READ_ONLY_MODE,
    "max_file_size": MAX_FILE_SIZE,
    "allowed_extensions": ALLOWED_EXTENSIONS if ALLOWED_EXTENSIONS else "all",
    "blocked_extensions": BLOCKED_EXTENSIONS,
    "max_search_file_size": MAX_SEARCH_FILE_SIZE
}

return json.dumps(filesystem_info, indent=2)
'''
            },
            {
                "name": "get_directory_tree",
                "uri": "fs://tree",
                "description": "Directory tree structure for current working directory",
                "parameters": "",
                "implementation": '''
# Get current working directory
current_path = "."
safe_path = await _validate_and_resolve_path(current_path)
if not safe_path or not safe_path.exists() or not safe_path.is_dir():
    return json.dumps({"error": f"Cannot access current directory"})

# Build tree structure
tree = await _build_directory_tree(safe_path, max_depth=3)

return json.dumps({
    "path": str(safe_path),
    "tree": tree
}, indent=2)
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "import os",
            "import base64",
            "from pathlib import Path",
            "from typing import List, Dict, Any, Optional",
            "import aiofiles",
            "import mimetypes",
            "import fnmatch",
            "import re",
            "import shutil",
            "from datetime import datetime",
        ]
    
    def get_init_code(self) -> str:
        allowed_paths = self.config.parameters.get("allowed_paths", [])
        read_only = self.config.parameters.get("read_only_mode", False)
        max_file_size = self.config.parameters.get("max_file_size", 10485760)  # 10MB
        allowed_extensions = self.config.parameters.get("allowed_extensions", [])
        blocked_extensions = self.config.parameters.get("blocked_extensions", [])
        
        return f'''
# Filesystem Configuration
ALLOWED_PATHS = [Path(p).resolve() for p in {allowed_paths or ["."]}]
READ_ONLY_MODE = {read_only}
MAX_FILE_SIZE = {max_file_size}  # bytes
MAX_SEARCH_FILE_SIZE = 1048576  # 1MB for content search
ALLOWED_EXTENSIONS = {allowed_extensions or []}
BLOCKED_EXTENSIONS = {blocked_extensions or [".exe", ".bat", ".cmd", ".sh", ".ps1"]}

# Common text file extensions for content search
TEXT_EXTENSIONS = {{
    '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
    '.csv', '.tsv', '.log', '.ini', '.cfg', '.conf', '.sql', '.sh', '.bat', '.ps1',
    '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.php', '.rb', '.go', '.rs'
}}

async def _validate_and_resolve_path(path: str, allow_create: bool = False) -> Optional[Path]:
    """Validate and resolve file path against allowed paths."""
    try:
        # Convert to Path object and resolve
        path_obj = Path(path).resolve()
        
        # Check against allowed paths
        for allowed_path in ALLOWED_PATHS:
            try:
                # Check if path is within allowed directory
                path_obj.relative_to(allowed_path)
                return path_obj
            except ValueError:
                continue
        
        # If we get here, path is not within any allowed directory
        logger.warning(f"Path access denied: {{path}} not in allowed paths")
        return None
        
    except Exception as e:
        logger.error(f"Path validation error: {{e}}")
        return None

async def _is_allowed_file_type(path: Path) -> bool:
    """Check if file type is allowed based on extension."""
    extension = path.suffix.lower()
    
    # Check blocked extensions first
    if extension in BLOCKED_EXTENSIONS:
        return False
    
    # If allowed extensions list is empty, allow all (except blocked)
    if not ALLOWED_EXTENSIONS:
        return True
    
    # Check if extension is in allowed list
    return extension in ALLOWED_EXTENSIONS

async def _is_text_file(path: Path) -> bool:
    """Check if file is likely a text file for content search."""
    extension = path.suffix.lower()
    return extension in TEXT_EXTENSIONS

async def _get_mime_type(path: Path) -> str:
    """Get MIME type of file."""
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type or "application/octet-stream"

async def _get_item_info(path: Path) -> Dict[str, Any]:
    """Get detailed information about a file or directory."""
    try:
        stat = path.stat()
        
        info = {{
            "name": path.name,
            "path": str(path),
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size if path.is_file() else None,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "permissions": oct(stat.st_mode)[-3:],
        }}
        
        if path.is_file():
            info.update({{
                "extension": path.suffix.lower(),
                "mime_type": await _get_mime_type(path)
            }})
        elif path.is_dir():
            # Count items in directory
            try:
                item_count = len(list(path.iterdir()))
                info["item_count"] = item_count
            except PermissionError:
                info["item_count"] = "access_denied"
        
        return info
        
    except Exception as e:
        return {{
            "name": path.name,
            "path": str(path),
            "type": "unknown",
            "error": str(e)
        }}

async def _list_directory_recursive(path: Path, include_hidden: bool, max_depth: int, current_depth: int = 0) -> List[Dict[str, Any]]:
    """Recursively list directory contents with depth limit."""
    items = []
    
    if current_depth >= max_depth:
        return items
    
    try:
        for item in path.iterdir():
            # Skip hidden files if not requested
            if not include_hidden and item.name.startswith('.'):
                continue
            
            item_info = await _get_item_info(item)
            item_info["depth"] = current_depth
            items.append(item_info)
            
            # Recurse into subdirectories
            if item.is_dir() and current_depth < max_depth - 1:
                sub_items = await _list_directory_recursive(item, include_hidden, max_depth, current_depth + 1)
                items.extend(sub_items)
    
    except PermissionError:
        logger.warning(f"Permission denied accessing: {{path}}")
    
    return items

async def _build_directory_tree(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
    """Build a tree structure of directory contents."""
    if current_depth >= max_depth:
        return {{"name": path.name, "type": "directory", "truncated": True}}
    
    try:
        children = []
        for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):
                continue  # Skip hidden files in tree view
            
            if item.is_dir():
                child = await _build_directory_tree(item, max_depth, current_depth + 1)
            else:
                child = {{
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size,
                    "extension": item.suffix.lower()
                }}
            
            children.append(child)
        
        return {{
            "name": path.name,
            "type": "directory",
            "children": children,
            "child_count": len(children)
        }}
        
    except PermissionError:
        return {{
            "name": path.name,
            "type": "directory",
            "error": "access_denied"
        }}

async def _confirm_deletion(path: Path) -> bool:
    """Check if deletion is allowed (safety mechanism)."""
    # Prevent deletion of important system directories
    dangerous_paths = [
        Path.home(),
        Path("/"),
        Path("/usr"),
        Path("/etc"),
        Path("/var"),
        Path("/sys"),
        Path("/proc"),
    ]
    
    for dangerous in dangerous_paths:
        try:
            path.relative_to(dangerous)
            # If we get here, path is within a dangerous directory
            if path == dangerous or len(path.parts) <= len(dangerous.parts) + 2:
                logger.warning(f"Deletion denied for protected path: {{path}}")
                return False
        except ValueError:
            continue
    
    return True
'''
    
    def get_cleanup_code(self) -> str:
        return '''
        # Cleanup filesystem resources
        logger.info("Cleaning up filesystem resources...")
'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Check allowed paths
        allowed_paths = self.config.parameters.get("allowed_paths", [])
        if not allowed_paths:
            errors.append("At least one allowed_path must be specified")
        else:
            for path in allowed_paths:
                if not os.path.exists(path):
                    errors.append(f"Allowed path does not exist: {path}")
                elif not os.path.isdir(path):
                    errors.append(f"Allowed path is not a directory: {path}")
        
        # Validate max file size
        max_file_size = self.config.parameters.get("max_file_size", 10485760)
        if not isinstance(max_file_size, int) or max_file_size < 1 or max_file_size > 1073741824:  # 1GB
            errors.append("max_file_size must be an integer between 1 and 1073741824 bytes (1GB)")
        
        # Validate extensions
        allowed_extensions = self.config.parameters.get("allowed_extensions", [])
        if allowed_extensions and not isinstance(allowed_extensions, list):
            errors.append("allowed_extensions must be a list of file extensions")
        
        blocked_extensions = self.config.parameters.get("blocked_extensions", [])
        if blocked_extensions and not isinstance(blocked_extensions, list):
            errors.append("blocked_extensions must be a list of file extensions")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "FS_ALLOWED_PATHS": "Comma-separated list of allowed directory paths",
            "FS_READ_ONLY": "Set to 'true' to enable read-only mode",
            "FS_MAX_FILE_SIZE": "Maximum file size in bytes (default: 10485760)",
            "FS_ALLOWED_EXTENSIONS": "Comma-separated list of allowed file extensions",
            "FS_BLOCKED_EXTENSIONS": "Comma-separated list of blocked file extensions",
        }
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text",
                "message": "Enter a description for your filesystem MCP server:",
                "default": "MCP server with filesystem backend",
            },
            {
                "name": "allowed_paths",
                "type": "text",
                "message": "Enter allowed directory paths (comma-separated):",
                "default": ".",
                "required": True,
            },
            {
                "name": "read_only_mode",
                "type": "bool",
                "message": "Enable read-only mode (no write/delete operations)?",
                "default": False,
            },
            {
                "name": "max_file_size",
                "type": "int",
                "message": "Enter maximum file size in bytes:",
                "default": 10485760,  # 10MB
            },
            {
                "name": "allowed_extensions",
                "type": "text",
                "message": "Enter allowed file extensions (comma-separated, empty for all):",
                "default": "",
            },
            {
                "name": "blocked_extensions",
                "type": "text",
                "message": "Enter blocked file extensions (comma-separated):",
                "default": ".exe,.bat,.cmd,.sh,.ps1",
            },
        ]