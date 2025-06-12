"""Email backend implementation for MCP servers."""

from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class EmailBackend(BaseBackend):
    """Backend for sending and receiving emails via SMTP/IMAP."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "email"
    
    @classmethod
    def get_description(cls) -> str:
        return "Send and receive emails via SMTP/IMAP with attachment support"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "aiosmtplib>=2.0.0",
            "imapclient>=2.3.0",
            "email-validator>=2.0.0",
            "aiofiles>=23.0.0",
            "python-magic>=0.4.27",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "send_email",
                "description": "Send email with optional attachments and HTML content",
                "parameters": "to: str, subject: str, body: str, cc: str = None, bcc: str = None, html_body: str = None, attachments: list = None",
                "return_type": "dict",
                "implementation": '''
    logger.info(f"Sending email to: {to}")
    
    # Validate email addresses
    if not await _validate_email_address(to):
        raise ValueError(f"Invalid recipient email address: {to}")
    
    # Validate CC and BCC if provided
    if cc and not await _validate_email_address(cc):
        raise ValueError(f"Invalid CC email address: {cc}")
    
    if bcc and not await _validate_email_address(bcc):
        raise ValueError(f"Invalid BCC email address: {bcc}")
    
    # Check rate limiting
    if not await _check_send_rate_limit():
        return {
            "success": False,
            "error": "Email sending rate limit exceeded",
            "rate_limit": True
        }
    
    # Create email message
    message = await _create_email_message(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
        attachments=attachments or []
    )
    
    # Send email via SMTP
    async with get_smtp_client() as smtp:
        await smtp.send_message(message)
    
    # Record sent email for rate limiting
    await _record_sent_email()
    
    return {
        "success": True,
        "message_id": message["Message-ID"],
        "to": to,
        "cc": cc,
        "bcc": bcc,
        "subject": subject,
        "timestamp": datetime.now().isoformat(),
        "attachments_count": len(attachments) if attachments else 0
    }
'''
            },
            {
                "name": "list_emails",
                "description": "List emails from a specific folder with filtering options",
                "parameters": "folder: str = 'INBOX', limit: int = 20, unread_only: bool = False, search_criteria: str = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Listing emails from folder: {folder}")
        
        # Connect to IMAP server
        async with get_imap_client() as imap:
            # Select folder
            await imap.select_folder(folder)
            
            # Build search criteria
            search_args = ['ALL']
            if unread_only:
                search_args = ['UNSEEN']
            
            if search_criteria:
                # Parse search criteria (simple implementation)
                if 'from:' in search_criteria.lower():
                    sender = search_criteria.lower().split('from:')[1].strip().split()[0]
                    search_args = ['FROM', sender]
                elif 'subject:' in search_criteria.lower():
                    subject = search_criteria.lower().split('subject:')[1].strip()
                    search_args = ['SUBJECT', subject]
            
            # Search for messages
            message_ids = await imap.search(search_args)
            
            # Limit results
            if limit and len(message_ids) > limit:
                message_ids = message_ids[-limit:]  # Get most recent
            
            # Fetch message details
            emails = []
            for msg_id in message_ids:
                try:
                    # Fetch message headers and basic info
                    msg_data = await imap.fetch([msg_id], ['ENVELOPE', 'FLAGS', 'RFC822.SIZE'])
                    envelope = msg_data[msg_id][b'ENVELOPE']
                    flags = msg_data[msg_id][b'FLAGS']
                    size = msg_data[msg_id][b'RFC822.SIZE']
                    
                    email_info = {
                        "id": msg_id,
                        "subject": envelope.subject.decode('utf-8') if envelope.subject else "",
                        "from": str(envelope.from_[0]) if envelope.from_ else "",
                        "to": [str(addr) for addr in envelope.to] if envelope.to else [],
                        "date": envelope.date.isoformat() if envelope.date else "",
                        "size": size,
                        "flags": [flag.decode() for flag in flags],
                        "unread": b'\\\\Seen' not in flags,
                        "folder": folder
                    }
                    
                    emails.append(email_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing message {msg_id}: {e}")
                    continue
            
            return {
                "success": True,
                "emails": emails,
                "folder": folder,
                "total_count": len(emails),
                "search_criteria": search_criteria,
                "unread_only": unread_only
            }
        
    except Exception as e:
        logger.error(f"Email listing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "folder": folder
        }
'''
            },
            {
                "name": "read_email",
                "description": "Read full content of a specific email including attachments",
                "parameters": "email_id: int, folder: str = 'INBOX', mark_as_read: bool = True",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Reading email ID: {email_id} from folder: {folder}")
        
        async with get_imap_client() as imap:
            # Select folder
            await imap.select_folder(folder)
            
            # Fetch full message
            msg_data = await imap.fetch([email_id], ['RFC822'])
            raw_message = msg_data[email_id][b'RFC822']
            
            # Parse email message
            import email
            from email.mime.multipart import MIMEMultipart
            
            message = email.message_from_bytes(raw_message)
            
            # Extract basic information
            email_info = {
                "id": email_id,
                "subject": message.get('Subject', ''),
                "from": message.get('From', ''),
                "to": message.get('To', ''),
                "cc": message.get('Cc', ''),
                "date": message.get('Date', ''),
                "message_id": message.get('Message-ID', ''),
                "folder": folder
            }
            
            # Extract body content
            body_text = ""
            body_html = ""
            attachments = []
            
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get('Content-Disposition', '')
                    
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        try:
                            body_text = part.get_payload(decode=True).decode('utf-8')
                        except:
                            body_text = str(part.get_payload())
                    
                    elif content_type == 'text/html' and 'attachment' not in content_disposition:
                        try:
                            body_html = part.get_payload(decode=True).decode('utf-8')
                        except:
                            body_html = str(part.get_payload())
                    
                    elif 'attachment' in content_disposition:
                        # Handle attachment
                        filename = part.get_filename()
                        if filename:
                            attachment_data = part.get_payload(decode=True)
                            attachment_info = {
                                "filename": filename,
                                "content_type": content_type,
                                "size": len(attachment_data) if attachment_data else 0,
                                "content_base64": base64.b64encode(attachment_data).decode('utf-8') if attachment_data else ""
                            }
                            attachments.append(attachment_info)
            else:
                # Single part message
                content_type = message.get_content_type()
                if content_type == 'text/plain':
                    body_text = message.get_payload(decode=True).decode('utf-8')
                elif content_type == 'text/html':
                    body_html = message.get_payload(decode=True).decode('utf-8')
            
            email_info.update({
                "body_text": body_text,
                "body_html": body_html,
                "attachments": attachments,
                "attachments_count": len(attachments)
            })
            
            # Mark as read if requested
            if mark_as_read:
                await imap.add_flags([email_id], ['\\\\Seen'])
            
            return {
                "success": True,
                "email": email_info
            }
        
    except Exception as e:
        logger.error(f"Email reading error: {e}")
        return {
            "success": False,
            "error": str(e),
            "email_id": email_id,
            "folder": folder
        }
'''
            },
            {
                "name": "search_emails",
                "description": "Advanced email search with multiple criteria",
                "parameters": "query: str, folder: str = 'INBOX', date_from: str = None, date_to: str = None, limit: int = 50",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Searching emails with query: {query}")
        
        async with get_imap_client() as imap:
            await imap.select_folder(folder)
            
            # Build search criteria
            search_args = []
            
            # Text search in subject and body
            if query:
                search_args.extend(['OR', 'SUBJECT', query, 'BODY', query])
            
            # Date range filtering
            if date_from:
                search_args.extend(['SINCE', date_from])
            
            if date_to:
                search_args.extend(['BEFORE', date_to])
            
            # Default to ALL if no criteria
            if not search_args:
                search_args = ['ALL']
            
            # Perform search
            message_ids = await imap.search(search_args)
            
            # Limit results
            if limit and len(message_ids) > limit:
                message_ids = message_ids[-limit:]
            
            # Fetch message summaries
            emails = []
            for msg_id in message_ids:
                try:
                    msg_data = await imap.fetch([msg_id], ['ENVELOPE', 'FLAGS'])
                    envelope = msg_data[msg_id][b'ENVELOPE']
                    flags = msg_data[msg_id][b'FLAGS']
                    
                    email_summary = {
                        "id": msg_id,
                        "subject": envelope.subject.decode('utf-8') if envelope.subject else "",
                        "from": str(envelope.from_[0]) if envelope.from_ else "",
                        "date": envelope.date.isoformat() if envelope.date else "",
                        "unread": b'\\\\Seen' not in flags
                    }
                    
                    emails.append(email_summary)
                    
                except Exception as e:
                    logger.warning(f"Error processing search result {msg_id}: {e}")
                    continue
            
            return {
                "success": True,
                "emails": emails,
                "query": query,
                "folder": folder,
                "total_results": len(emails),
                "date_from": date_from,
                "date_to": date_to
            }
        
    except Exception as e:
        logger.error(f"Email search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "folder": folder
        }
'''
            },
            {
                "name": "manage_folders",
                "description": "List, create, or manage email folders",
                "parameters": "action: str, folder_name: str = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Managing folders - action: {action}")
        
        async with get_imap_client() as imap:
            if action == "list":
                # List all folders
                folders = await imap.list_folders()
                folder_list = []
                
                for folder in folders:
                    folder_info = {
                        "name": folder.name,
                        "separator": folder.separator,
                        "flags": list(folder.flags)
                    }
                    folder_list.append(folder_info)
                
                return {
                    "success": True,
                    "action": "list",
                    "folders": folder_list,
                    "total_folders": len(folder_list)
                }
            
            elif action == "create" and folder_name:
                # Create new folder
                await imap.create_folder(folder_name)
                return {
                    "success": True,
                    "action": "create",
                    "folder_name": folder_name,
                    "message": f"Folder '{folder_name}' created successfully"
                }
            
            elif action == "delete" and folder_name:
                # Delete folder (be careful!)
                await imap.delete_folder(folder_name)
                return {
                    "success": True,
                    "action": "delete", 
                    "folder_name": folder_name,
                    "message": f"Folder '{folder_name}' deleted successfully"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Invalid action or missing folder_name. Action: {action}",
                    "supported_actions": ["list", "create", "delete"]
                }
        
    except Exception as e:
        logger.error(f"Folder management error: {e}")
        return {
            "success": False,
            "error": str(e),
            "action": action,
            "folder_name": folder_name
        }
'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_email_config",
                "uri": "email://config",
                "description": "Email server configuration and connection status",
                "parameters": "",
                "implementation": '''
    try:
        config_info = {
            "smtp_server": SMTP_HOST,
            "smtp_port": SMTP_PORT,
            "imap_server": IMAP_HOST,
            "imap_port": IMAP_PORT,
            "username": USERNAME,
            "use_tls": USE_TLS,
            "rate_limit": {
                "max_emails_per_hour": MAX_EMAILS_PER_HOUR,
                "remaining": await _get_remaining_email_quota()
            },
            "connection_status": await _check_email_connection()
        }
        
        return json.dumps(config_info, indent=2)
        
    except Exception as e:
        logger.error(f"Email config resource error: {e}")
        return json.dumps({"error": str(e)})
'''
            },
            {
                "name": "get_folder_stats",
                "uri": "email://stats/{folder}",
                "description": "Statistics for a specific email folder",
                "parameters": "folder: str",
                "implementation": '''
    try:
        async with get_imap_client() as imap:
            await imap.select_folder(folder)
            
            # Get folder statistics
            total_messages = len(await imap.search(['ALL']))
            unread_messages = len(await imap.search(['UNSEEN']))
            recent_messages = len(await imap.search(['RECENT']))
            
            stats = {
                "folder": folder,
                "total_messages": total_messages,
                "unread_messages": unread_messages,
                "recent_messages": recent_messages,
                "read_messages": total_messages - unread_messages,
                "last_updated": datetime.now().isoformat()
            }
            
            return json.dumps(stats, indent=2)
        
    except Exception as e:
        logger.error(f"Folder stats resource error: {e}")
        return json.dumps({"error": str(e), "folder": folder})
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "import base64",
            "import asyncio",
            "from datetime import datetime, timedelta",
            "from contextlib import asynccontextmanager",
            "from typing import List, Dict, Any, Optional",
            "import aiosmtplib",
            "from imapclient import IMAPClient",
            "import email",
            "from email.mime.text import MIMEText",
            "from email.mime.multipart import MIMEMultipart", 
            "from email.mime.base import MIMEBase",
            "from email import encoders",
            "import os",
            "import re",
            "import uuid",
            "from email_validator import validate_email, EmailNotValidError",
        ]
    
    def get_init_code(self) -> str:
        smtp_host = self.config.parameters.get("smtp_host", "")
        smtp_port = self.config.parameters.get("smtp_port", 587)
        imap_host = self.config.parameters.get("imap_host", "")
        imap_port = self.config.parameters.get("imap_port", 993)
        use_tls = self.config.parameters.get("use_tls", True)
        max_emails_per_hour = self.config.parameters.get("max_emails_per_hour", 50)
        
        return f'''
# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "{smtp_host}")
SMTP_PORT = {smtp_port}
IMAP_HOST = os.getenv("IMAP_HOST", "{imap_host}")
IMAP_PORT = {imap_port}
USERNAME = os.getenv("EMAIL_USERNAME", "")
PASSWORD = os.getenv("EMAIL_PASSWORD", "")
USE_TLS = {use_tls}

# Rate limiting
MAX_EMAILS_PER_HOUR = {max_emails_per_hour}
email_send_history = []

@asynccontextmanager
async def get_smtp_client():
    """Get SMTP client for sending emails."""
    smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT)
    try:
        await smtp.connect()
        if USE_TLS:
            await smtp.starttls()
        await smtp.login(USERNAME, PASSWORD)
        yield smtp
    finally:
        await smtp.quit()

@asynccontextmanager
async def get_imap_client():
    """Get IMAP client for reading emails."""
    # Note: Using synchronous IMAPClient in async context
    # In production, consider using an async IMAP library
    imap = IMAPClient(IMAP_HOST, port=IMAP_PORT, ssl=True)
    try:
        imap.login(USERNAME, PASSWORD)
        yield imap
    finally:
        imap.logout()

async def _validate_email_address(email_addr: str) -> bool:
    """Validate email address format."""
    try:
        validate_email(email_addr)
        return True
    except EmailNotValidError:
        return False

async def _check_send_rate_limit() -> bool:
    """Check if email sending is within rate limits."""
    current_time = datetime.now()
    hour_ago = current_time - timedelta(hours=1)
    
    # Clean old entries
    global email_send_history
    email_send_history = [t for t in email_send_history if t > hour_ago]
    
    return len(email_send_history) < MAX_EMAILS_PER_HOUR

async def _record_sent_email() -> None:
    """Record email send timestamp for rate limiting."""
    global email_send_history
    email_send_history.append(datetime.now())

async def _get_remaining_email_quota() -> int:
    """Get remaining emails in current hour quota."""
    current_time = datetime.now()
    hour_ago = current_time - timedelta(hours=1)
    
    recent_sends = [t for t in email_send_history if t > hour_ago]
    return max(0, MAX_EMAILS_PER_HOUR - len(recent_sends))

async def _create_email_message(to: str, subject: str, body: str, cc: str = None, 
                               bcc: str = None, html_body: str = None, 
                               attachments: List[Dict] = None) -> MIMEMultipart:
    """Create email message with attachments."""
    msg = MIMEMultipart('alternative')
    
    # Set headers
    msg['From'] = USERNAME
    msg['To'] = to
    msg['Subject'] = subject
    
    if cc:
        msg['Cc'] = cc
    if bcc:
        msg['Bcc'] = bcc
    
    # Add message ID
    import uuid
    msg['Message-ID'] = f"<{{uuid.uuid4()}}@{{SMTP_HOST}}>"
    
    # Add text body
    if body:
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
    
    # Add HTML body if provided
    if html_body:
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
    
    # Add attachments
    if attachments:
        for attachment in attachments:
            if isinstance(attachment, dict) and 'filename' in attachment:
                # Attachment with metadata
                filename = attachment['filename']
                content = attachment.get('content', '')
                content_type = attachment.get('content_type', 'application/octet-stream')
                
                # Decode base64 content if needed
                if attachment.get('encoding') == 'base64':
                    content = base64.b64decode(content)
                elif isinstance(content, str):
                    content = content.encode('utf-8')
                
                part = MIMEBase(*content_type.split('/'))
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "{{filename}}"'
                )
                msg.attach(part)
    
    return msg

async def _check_email_connection() -> Dict[str, Any]:
    """Check email server connection status."""
    status = {{
        "smtp_connected": False,
        "imap_connected": False,
        "last_check": datetime.now().isoformat()
    }}
    
    # Test SMTP connection
    try:
        async with get_smtp_client():
            status["smtp_connected"] = True
    except Exception as e:
        status["smtp_error"] = str(e)
    
    # Test IMAP connection  
    try:
        async with get_imap_client():
            status["imap_connected"] = True
    except Exception as e:
        status["imap_error"] = str(e)
    
    return status
'''
    
    def get_cleanup_code(self) -> str:
        return '''
        # Cleanup email connections
        logger.info("Cleaning up email connections...")
'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Check required SMTP parameters
        smtp_host = self.config.parameters.get("smtp_host")
        if not smtp_host:
            errors.append("smtp_host is required")
        
        # Check required IMAP parameters
        imap_host = self.config.parameters.get("imap_host")
        if not imap_host:
            errors.append("imap_host is required")
        
        # Validate ports
        smtp_port = self.config.parameters.get("smtp_port", 587)
        if not isinstance(smtp_port, int) or smtp_port < 1 or smtp_port > 65535:
            errors.append("smtp_port must be a valid port number (1-65535)")
        
        imap_port = self.config.parameters.get("imap_port", 993)
        if not isinstance(imap_port, int) or imap_port < 1 or imap_port > 65535:
            errors.append("imap_port must be a valid port number (1-65535)")
        
        # Validate rate limit
        max_emails = self.config.parameters.get("max_emails_per_hour", 50)
        if not isinstance(max_emails, int) or max_emails < 1 or max_emails > 1000:
            errors.append("max_emails_per_hour must be an integer between 1 and 1000")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "SMTP_HOST": "SMTP server hostname (e.g., smtp.gmail.com)",
            "IMAP_HOST": "IMAP server hostname (e.g., imap.gmail.com)",
            "EMAIL_USERNAME": "Email account username/email address",
            "EMAIL_PASSWORD": "Email account password or app password",
            "EMAIL_MAX_PER_HOUR": "Maximum emails to send per hour (optional, default: 50)",
        }
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text", 
                "message": "Enter a description for your email MCP server:",
                "default": "MCP server with email backend",
            },
            {
                "name": "smtp_host",
                "type": "text",
                "message": "Enter SMTP server hostname:",
                "default": "smtp.gmail.com",
                "required": True,
            },
            {
                "name": "smtp_port",
                "type": "int",
                "message": "Enter SMTP server port:",
                "default": 587,
            },
            {
                "name": "imap_host", 
                "type": "text",
                "message": "Enter IMAP server hostname:",
                "default": "imap.gmail.com",
                "required": True,
            },
            {
                "name": "imap_port",
                "type": "int",
                "message": "Enter IMAP server port:",
                "default": 993,
            },
            {
                "name": "use_tls",
                "type": "bool",
                "message": "Use TLS encryption?",
                "default": True,
            },
            {
                "name": "max_emails_per_hour",
                "type": "int", 
                "message": "Enter maximum emails to send per hour:",
                "default": 50,
            },
        ]