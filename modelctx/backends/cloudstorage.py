"""Cloud storage backend implementation for MCP servers."""

from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class CloudStorageBackend(BaseBackend):
    """Backend for cloud storage services (AWS S3, Google Cloud Storage, Azure Blob)."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "cloudstorage"
    
    @classmethod
    def get_description(cls) -> str:
        return "Connect to cloud storage services (AWS S3, Google Cloud Storage, Azure Blob)"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "boto3>=1.26.0",
            "google-cloud-storage>=2.10.0", 
            "azure-storage-blob>=12.17.0",
            "aiofiles>=23.0.0",
            "python-magic>=0.4.27",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "upload_file",
                "description": "Upload file to cloud storage with metadata and access control",
                "parameters": "local_path: str, remote_key: str, bucket: str = None, metadata: dict = None, public: bool = False",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Uploading file: {{local_path}} -> {{remote_key}}")
        
        # Validate local file exists
        import os
        if not os.path.exists(local_path):
            raise ValueError(f"Local file does not exist: {{local_path}}")
        
        # Get file info
        file_size = os.path.getsize(local_path)
        if file_size > MAX_FILE_SIZE:
            return {
                "success": False,
                "error": f"File too large: {{file_size}} bytes (max: {{MAX_FILE_SIZE}})",
                "file_size": file_size,
                "max_size": MAX_FILE_SIZE
            }
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Get storage client
        client = get_storage_client()
        
        # Upload based on provider
        if CLOUD_PROVIDER == "aws":
            result = await _upload_to_s3(client, local_path, remote_key, target_bucket, metadata, public)
        elif CLOUD_PROVIDER == "gcp":
            result = await _upload_to_gcs(client, local_path, remote_key, target_bucket, metadata, public)
        elif CLOUD_PROVIDER == "azure":
            result = await _upload_to_azure(client, local_path, remote_key, target_bucket, metadata, public)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        return {
            "success": True,
            "local_path": local_path,
            "remote_key": remote_key,
            "bucket": target_bucket,
            "file_size": file_size,
            "provider": CLOUD_PROVIDER,
            "public": public,
            "metadata": metadata,
            **result
        }
        
    except Exception as e:
        logger.error(f"Upload error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "local_path": local_path,
            "remote_key": remote_key
        }
'''
            },
            {
                "name": "download_file",
                "description": "Download file from cloud storage to local path",
                "parameters": "remote_key: str, local_path: str, bucket: str = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Downloading file: {{remote_key}} -> {{local_path}}")
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Validate local directory exists
        import os
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        
        # Get storage client
        client = get_storage_client()
        
        # Download based on provider
        if CLOUD_PROVIDER == "aws":
            result = await _download_from_s3(client, remote_key, local_path, target_bucket)
        elif CLOUD_PROVIDER == "gcp":
            result = await _download_from_gcs(client, remote_key, local_path, target_bucket)
        elif CLOUD_PROVIDER == "azure":
            result = await _download_from_azure(client, remote_key, local_path, target_bucket)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        # Get downloaded file info
        file_size = os.path.getsize(local_path)
        
        return {
            "success": True,
            "remote_key": remote_key,
            "local_path": local_path,
            "bucket": target_bucket,
            "file_size": file_size,
            "provider": CLOUD_PROVIDER,
            **result
        }
        
    except Exception as e:
        logger.error(f"Download error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "remote_key": remote_key,
            "local_path": local_path
        }
'''
            },
            {
                "name": "list_objects",
                "description": "List objects in cloud storage bucket with filtering and pagination",
                "parameters": "prefix: str = '', bucket: str = None, max_keys: int = 100, recursive: bool = True",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Listing objects with prefix: {{prefix}}")
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Get storage client
        client = get_storage_client()
        
        # List based on provider
        if CLOUD_PROVIDER == "aws":
            objects = await _list_s3_objects(client, target_bucket, prefix, max_keys, recursive)
        elif CLOUD_PROVIDER == "gcp":
            objects = await _list_gcs_objects(client, target_bucket, prefix, max_keys, recursive)
        elif CLOUD_PROVIDER == "azure":
            objects = await _list_azure_objects(client, target_bucket, prefix, max_keys, recursive)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        # Process and format objects
        formatted_objects = []
        total_size = 0
        
        for obj in objects:
            obj_info = {
                "key": obj.get("key", ""),
                "size": obj.get("size", 0),
                "last_modified": obj.get("last_modified", ""),
                "etag": obj.get("etag", ""),
                "storage_class": obj.get("storage_class", ""),
                "content_type": obj.get("content_type", "")
            }
            formatted_objects.append(obj_info)
            total_size += obj_info["size"]
        
        return {
            "success": True,
            "objects": formatted_objects,
            "bucket": target_bucket,
            "prefix": prefix,
            "count": len(formatted_objects),
            "total_size": total_size,
            "provider": CLOUD_PROVIDER,
            "recursive": recursive,
            "truncated": len(formatted_objects) >= max_keys
        }
        
    except Exception as e:
        logger.error(f"List objects error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "bucket": target_bucket,
            "prefix": prefix
        }
'''
            },
            {
                "name": "delete_object",
                "description": "Delete object from cloud storage",
                "parameters": "remote_key: str, bucket: str = None, confirm: bool = True",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Deleting object: {{remote_key}}")
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Safety check for confirmation
        if confirm and not await _confirm_deletion(remote_key):
            return {
                "success": False,
                "error": "Deletion not confirmed or object is protected",
                "remote_key": remote_key
            }
        
        # Get storage client
        client = get_storage_client()
        
        # Check if object exists first
        exists = await _check_object_exists(client, target_bucket, remote_key)
        if not exists:
            return {
                "success": False,
                "error": f"Object does not exist: {{remote_key}}",
                "remote_key": remote_key,
                "bucket": target_bucket
            }
        
        # Delete based on provider
        if CLOUD_PROVIDER == "aws":
            result = await _delete_from_s3(client, remote_key, target_bucket)
        elif CLOUD_PROVIDER == "gcp":
            result = await _delete_from_gcs(client, remote_key, target_bucket)
        elif CLOUD_PROVIDER == "azure":
            result = await _delete_from_azure(client, remote_key, target_bucket)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        return {
            "success": True,
            "remote_key": remote_key,
            "bucket": target_bucket,
            "provider": CLOUD_PROVIDER,
            **result
        }
        
    except Exception as e:
        logger.error(f"Delete error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "remote_key": remote_key,
            "bucket": target_bucket
        }
'''
            },
            {
                "name": "get_object_info",
                "description": "Get detailed information about a cloud storage object",
                "parameters": "remote_key: str, bucket: str = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Getting object info: {{remote_key}}")
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Get storage client
        client = get_storage_client()
        
        # Get info based on provider
        if CLOUD_PROVIDER == "aws":
            obj_info = await _get_s3_object_info(client, remote_key, target_bucket)
        elif CLOUD_PROVIDER == "gcp":
            obj_info = await _get_gcs_object_info(client, remote_key, target_bucket)
        elif CLOUD_PROVIDER == "azure":
            obj_info = await _get_azure_object_info(client, remote_key, target_bucket)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        if not obj_info:
            return {
                "success": False,
                "error": f"Object not found: {{remote_key}}",
                "remote_key": remote_key,
                "bucket": target_bucket
            }
        
        return {
            "success": True,
            "remote_key": remote_key,
            "bucket": target_bucket,
            "provider": CLOUD_PROVIDER,
            **obj_info
        }
        
    except Exception as e:
        logger.error(f"Get object info error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "remote_key": remote_key,
            "bucket": target_bucket
        }
'''
            },
            {
                "name": "generate_presigned_url",
                "description": "Generate presigned URL for temporary access to cloud storage object",
                "parameters": "remote_key: str, expiration: int = 3600, operation: str = 'GET', bucket: str = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Generating presigned URL for: {{remote_key}}")
        
        # Use default bucket if not specified
        target_bucket = bucket or DEFAULT_BUCKET
        
        # Validate expiration time
        if expiration < 60 or expiration > 604800:  # 1 minute to 7 days
            raise ValueError("Expiration must be between 60 seconds and 7 days")
        
        # Validate operation
        if operation.upper() not in ['GET', 'PUT', 'DELETE']:
            raise ValueError("Operation must be GET, PUT, or DELETE")
        
        # Get storage client
        client = get_storage_client()
        
        # Generate URL based on provider
        if CLOUD_PROVIDER == "aws":
            url_info = await _generate_s3_presigned_url(client, remote_key, target_bucket, expiration, operation)
        elif CLOUD_PROVIDER == "gcp":
            url_info = await _generate_gcs_presigned_url(client, remote_key, target_bucket, expiration, operation)
        elif CLOUD_PROVIDER == "azure":
            url_info = await _generate_azure_presigned_url(client, remote_key, target_bucket, expiration, operation)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        return {
            "success": True,
            "remote_key": remote_key,
            "bucket": target_bucket,
            "operation": operation.upper(),
            "expiration_seconds": expiration,
            "expires_at": (datetime.now() + timedelta(seconds=expiration)).isoformat(),
            "provider": CLOUD_PROVIDER,
            **url_info
        }
        
    except Exception as e:
        logger.error(f"Presigned URL error: {{e}}")
        return {
            "success": False,
            "error": str(e),
            "remote_key": remote_key,
            "operation": operation
        }
'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_storage_config",
                "uri": "storage://config",
                "description": "Cloud storage configuration and connection status",
                "parameters": "",
                "implementation": '''
    try:
        config_info = {
            "provider": CLOUD_PROVIDER,
            "default_bucket": DEFAULT_BUCKET,
            "region": REGION,
            "max_file_size": MAX_FILE_SIZE,
            "allowed_buckets": ALLOWED_BUCKETS if ALLOWED_BUCKETS else "all",
            "connection_status": await _check_storage_connection()
        }
        
        return json.dumps(config_info, indent=2)
        
    except Exception as e:
        logger.error(f"Storage config resource error: {{e}}")
        return json.dumps({"error": str(e)})
'''
            },
            {
                "name": "get_bucket_info",
                "uri": "storage://bucket/{bucket_name}",
                "description": "Information about a specific storage bucket",
                "parameters": "bucket_name: str",
                "implementation": '''
    try:
        client = get_storage_client()
        
        # Get bucket info based on provider
        if CLOUD_PROVIDER == "aws":
            bucket_info = await _get_s3_bucket_info(client, bucket_name)
        elif CLOUD_PROVIDER == "gcp":
            bucket_info = await _get_gcs_bucket_info(client, bucket_name)
        elif CLOUD_PROVIDER == "azure":
            bucket_info = await _get_azure_container_info(client, bucket_name)
        else:
            raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")
        
        return json.dumps({
            "bucket_name": bucket_name,
            "provider": CLOUD_PROVIDER,
            **bucket_info
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Bucket info resource error: {{e}}")
        return json.dumps({"error": str(e), "bucket_name": bucket_name})
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "import os",
            "import asyncio",
            "from datetime import datetime, timedelta",
            "from typing import Dict, List, Any, Optional",
            "import mimetypes",
            "# Cloud provider imports (conditional)",
            "try:",
            "    import boto3",
            "    from botocore.exceptions import ClientError, BotoCoreError",
            "except ImportError:",
            "    boto3 = None",
            "",
            "try:",
            "    from google.cloud import storage as gcs",
            "    from google.api_core import exceptions as gcs_exceptions",
            "except ImportError:",
            "    gcs = None",
            "",
            "try:",
            "    from azure.storage.blob import BlobServiceClient",
            "    from azure.core.exceptions import AzureError",
            "except ImportError:",
            "    BlobServiceClient = None",
        ]
    
    def get_init_code(self) -> str:
        provider = self.config.parameters.get("cloud_provider", "aws")
        bucket = self.config.parameters.get("default_bucket", "")
        region = self.config.parameters.get("region", "us-east-1")
        max_file_size = self.config.parameters.get("max_file_size", 104857600)  # 100MB
        allowed_buckets = self.config.parameters.get("allowed_buckets", [])
        
        return f'''
# Cloud Storage Configuration
CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER", "{provider}").lower()
DEFAULT_BUCKET = os.getenv("DEFAULT_BUCKET", "{bucket}")
REGION = os.getenv("CLOUD_REGION", "{region}")
MAX_FILE_SIZE = {max_file_size}  # bytes
ALLOWED_BUCKETS = {allowed_buckets or []}

# Provider-specific credentials
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")

GCP_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")

AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME", "")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY", "")
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")

def get_storage_client():
    """Get storage client based on configured provider."""
    if CLOUD_PROVIDER == "aws":
        if not boto3:
            raise ImportError("boto3 is required for AWS S3. Install with: pip install boto3")
        
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            aws_session_token=AWS_SESSION_TOKEN,
            region_name=REGION
        )
        return session.client('s3')
    
    elif CLOUD_PROVIDER == "gcp":
        if not gcs:
            raise ImportError("google-cloud-storage is required for GCS. Install with: pip install google-cloud-storage")
        
        if GCP_CREDENTIALS_PATH:
            return gcs.Client.from_service_account_json(GCP_CREDENTIALS_PATH, project=GCP_PROJECT_ID)
        else:
            # Use default credentials (ADC)
            return gcs.Client(project=GCP_PROJECT_ID)
    
    elif CLOUD_PROVIDER == "azure":
        if not BlobServiceClient:
            raise ImportError("azure-storage-blob is required for Azure. Install with: pip install azure-storage-blob")
        
        if AZURE_CONNECTION_STRING:
            return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        elif AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
            account_url = f"https://{{AZURE_ACCOUNT_NAME}}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=AZURE_ACCOUNT_KEY)
        else:
            raise ValueError("Azure credentials not configured")
    
    else:
        raise ValueError(f"Unsupported cloud provider: {{CLOUD_PROVIDER}}")

# AWS S3 Functions
async def _upload_to_s3(client, local_path: str, remote_key: str, bucket: str, metadata: dict, public: bool) -> dict:
    """Upload file to AWS S3."""
    extra_args = {{}}
    if metadata:
        extra_args['Metadata'] = metadata
    if public:
        extra_args['ACL'] = 'public-read'
    
    # Detect content type
    content_type, _ = mimetypes.guess_type(local_path)
    if content_type:
        extra_args['ContentType'] = content_type
    
    try:
        client.upload_file(local_path, bucket, remote_key, ExtraArgs=extra_args)
        
        # Get uploaded object info
        response = client.head_object(Bucket=bucket, Key=remote_key)
        
        return {{
            "etag": response.get('ETag', '').strip('"'),
            "last_modified": response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
            "content_type": response.get('ContentType', ''),
            "server_side_encryption": response.get('ServerSideEncryption', ''),
            "version_id": response.get('VersionId', '')
        }}
    except ClientError as e:
        raise Exception(f"S3 upload error: {{e}}")

async def _download_from_s3(client, remote_key: str, local_path: str, bucket: str) -> dict:
    """Download file from AWS S3."""
    try:
        response = client.download_file(bucket, remote_key, local_path)
        
        # Get object metadata
        obj_info = client.head_object(Bucket=bucket, Key=remote_key)
        
        return {{
            "etag": obj_info.get('ETag', '').strip('"'),
            "last_modified": obj_info.get('LastModified', '').isoformat() if obj_info.get('LastModified') else '',
            "content_type": obj_info.get('ContentType', '')
        }}
    except ClientError as e:
        raise Exception(f"S3 download error: {{e}}")

async def _list_s3_objects(client, bucket: str, prefix: str, max_keys: int, recursive: bool) -> List[dict]:
    """List objects in S3 bucket."""
    try:
        kwargs = {{
            'Bucket': bucket,
            'MaxKeys': max_keys
        }}
        if prefix:
            kwargs['Prefix'] = prefix
        if not recursive:
            kwargs['Delimiter'] = '/'
        
        response = client.list_objects_v2(**kwargs)
        
        objects = []
        for obj in response.get('Contents', []):
            objects.append({{
                "key": obj['Key'],
                "size": obj['Size'],
                "last_modified": obj['LastModified'].isoformat(),
                "etag": obj['ETag'].strip('"'),
                "storage_class": obj.get('StorageClass', 'STANDARD')
            }})
        
        return objects
    except ClientError as e:
        raise Exception(f"S3 list error: {{e}}")

async def _delete_from_s3(client, remote_key: str, bucket: str) -> dict:
    """Delete object from S3."""
    try:
        response = client.delete_object(Bucket=bucket, Key=remote_key)
        return {{
            "delete_marker": response.get('DeleteMarker', False),
            "version_id": response.get('VersionId', '')
        }}
    except ClientError as e:
        raise Exception(f"S3 delete error: {{e}}")

async def _get_s3_object_info(client, remote_key: str, bucket: str) -> dict:
    """Get S3 object information."""
    try:
        response = client.head_object(Bucket=bucket, Key=remote_key)
        return {{
            "size": response.get('ContentLength', 0),
            "last_modified": response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
            "etag": response.get('ETag', '').strip('"'),
            "content_type": response.get('ContentType', ''),
            "metadata": response.get('Metadata', {{}}),
            "storage_class": response.get('StorageClass', 'STANDARD'),
            "server_side_encryption": response.get('ServerSideEncryption', '')
        }}
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        raise Exception(f"S3 head object error: {{e}}")

async def _generate_s3_presigned_url(client, remote_key: str, bucket: str, expiration: int, operation: str) -> dict:
    """Generate S3 presigned URL."""
    try:
        method_map = {{
            'GET': 'get_object',
            'PUT': 'put_object',
            'DELETE': 'delete_object'
        }}
        
        url = client.generate_presigned_url(
            method_map[operation.upper()],
            Params={{'Bucket': bucket, 'Key': remote_key}},
            ExpiresIn=expiration
        )
        
        return {{"presigned_url": url}}
    except ClientError as e:
        raise Exception(f"S3 presigned URL error: {{e}}")

async def _get_s3_bucket_info(client, bucket_name: str) -> dict:
    """Get S3 bucket information."""
    try:
        # Get bucket location
        location = client.get_bucket_location(Bucket=bucket_name)
        
        # Get bucket versioning
        versioning = client.get_bucket_versioning(Bucket=bucket_name)
        
        return {{
            "location": location.get('LocationConstraint', 'us-east-1'),
            "versioning": versioning.get('Status', 'Disabled'),
            "mfa_delete": versioning.get('MfaDelete', 'Disabled'),
            "exists": True
        }}
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            return {{"exists": False}}
        raise Exception(f"S3 bucket info error: {{e}}")

# GCS Functions (Google Cloud Storage)
async def _upload_to_gcs(client, local_path: str, remote_key: str, bucket: str, metadata: dict, public: bool) -> dict:
    """Upload file to Google Cloud Storage."""
    try:
        bucket_obj = client.bucket(bucket)
        blob = bucket_obj.blob(remote_key)
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        # Detect content type
        content_type, _ = mimetypes.guess_type(local_path)
        if content_type:
            blob.content_type = content_type
        
        # Upload file
        blob.upload_from_filename(local_path)
        
        # Make public if requested
        if public:
            blob.make_public()
        
        return {{
            "etag": blob.etag,
            "last_modified": blob.updated.isoformat() if blob.updated else '',
            "content_type": blob.content_type or '',
            "public_url": blob.public_url if public else '',
            "generation": str(blob.generation)
        }}
    except Exception as e:
        raise Exception(f"GCS upload error: {{e}}")

# Azure Blob Functions
async def _upload_to_azure(client, local_path: str, remote_key: str, container: str, metadata: dict, public: bool) -> dict:
    """Upload file to Azure Blob Storage."""
    try:
        blob_client = client.get_blob_client(container=container, blob=remote_key)
        
        # Detect content type
        content_type, _ = mimetypes.guess_type(local_path)
        
        with open(local_path, 'rb') as data:
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_type=content_type,
                metadata=metadata
            )
        
        # Get blob properties
        props = blob_client.get_blob_properties()
        
        return {{
            "etag": props.etag.strip('"'),
            "last_modified": props.last_modified.isoformat(),
            "content_type": props.content_settings.content_type or '',
            "blob_type": props.blob_type
        }}
    except Exception as e:
        raise Exception(f"Azure upload error: {{e}}")

async def _check_object_exists(client, bucket: str, remote_key: str) -> bool:
    """Check if object exists in storage."""
    try:
        if CLOUD_PROVIDER == "aws":
            client.head_object(Bucket=bucket, Key=remote_key)
        elif CLOUD_PROVIDER == "gcp":
            bucket_obj = client.bucket(bucket)
            blob = bucket_obj.blob(remote_key)
            return blob.exists()
        elif CLOUD_PROVIDER == "azure":
            blob_client = client.get_blob_client(container=bucket, blob=remote_key)
            return blob_client.exists()
        
        return True
    except:
        return False

async def _confirm_deletion(remote_key: str) -> bool:
    """Check if deletion is allowed (safety mechanism)."""
    # Prevent deletion of important files
    protected_patterns = [
        'config/',
        'backup/',
        '.env',
        'credentials'
    ]
    
    for pattern in protected_patterns:
        if pattern in remote_key.lower():
            logger.warning(f"Deletion denied for protected object: {{remote_key}}")
            return False
    
    return True

async def _check_storage_connection() -> Dict[str, Any]:
    """Check cloud storage connection status."""
    try:
        client = get_storage_client()
        
        if CLOUD_PROVIDER == "aws":
            # Try to list buckets
            client.list_buckets()
        elif CLOUD_PROVIDER == "gcp":
            # Try to list buckets
            list(client.list_buckets())
        elif CLOUD_PROVIDER == "azure":
            # Try to list containers
            list(client.list_containers())
        
        return {{
            "connected": True,
            "provider": CLOUD_PROVIDER,
            "last_check": datetime.now().isoformat()
        }}
    except Exception as e:
        return {{
            "connected": False,
            "provider": CLOUD_PROVIDER,
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }}
'''
    
    def get_cleanup_code(self) -> str:
        return '''
        # Cleanup cloud storage connections
        logger.info("Cleaning up cloud storage connections...")
'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Check cloud provider
        provider = self.config.parameters.get("cloud_provider", "")
        if provider not in ["aws", "gcp", "azure"]:
            errors.append("cloud_provider must be one of: aws, gcp, azure")
        
        # Check default bucket
        bucket = self.config.parameters.get("default_bucket", "")
        if not bucket:
            errors.append("default_bucket is required")
        
        # Validate region
        region = self.config.parameters.get("region", "")
        if not region:
            errors.append("region is required")
        
        # Validate max file size
        max_size = self.config.parameters.get("max_file_size", 104857600)
        if not isinstance(max_size, int) or max_size < 1 or max_size > 5368709120:  # 5GB
            errors.append("max_file_size must be an integer between 1 and 5368709120 bytes (5GB)")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "CLOUD_PROVIDER": "Cloud provider: aws, gcp, or azure",
            "DEFAULT_BUCKET": "Default bucket/container name",
            "CLOUD_REGION": "Cloud region (e.g., us-east-1, us-central1, eastus)",
            "AWS_ACCESS_KEY_ID": "AWS access key ID",
            "AWS_SECRET_ACCESS_KEY": "AWS secret access key",
            "AWS_SESSION_TOKEN": "AWS session token (optional)",
            "GOOGLE_APPLICATION_CREDENTIALS": "Path to GCP service account JSON file",
            "GCP_PROJECT_ID": "Google Cloud project ID",
            "AZURE_ACCOUNT_NAME": "Azure storage account name",
            "AZURE_ACCOUNT_KEY": "Azure storage account key",
            "AZURE_STORAGE_CONNECTION_STRING": "Azure storage connection string",
        }
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text",
                "message": "Enter a description for your cloud storage MCP server:",
                "default": "MCP server with cloud storage backend",
            },
            {
                "name": "cloud_provider",
                "type": "choice",
                "message": "Select cloud storage provider:",
                "choices": ["aws", "gcp", "azure"],
                "default": "aws",
                "required": True,
            },
            {
                "name": "default_bucket",
                "type": "text",
                "message": "Enter default bucket/container name:",
                "default": "my-mcp-bucket",
                "required": True,
            },
            {
                "name": "region",
                "type": "text",
                "message": "Enter cloud region:",
                "default": "us-east-1",
                "required": True,
            },
            {
                "name": "max_file_size",
                "type": "int",
                "message": "Enter maximum file size in bytes:",
                "default": 104857600,  # 100MB
            },
            {
                "name": "allowed_buckets",
                "type": "text",
                "message": "Enter allowed buckets (comma-separated, empty for all):",
                "default": "",
            },
        ]