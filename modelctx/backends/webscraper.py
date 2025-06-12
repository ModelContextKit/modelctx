"""Web scraper backend implementation for MCP servers."""

from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class WebScraperBackend(BaseBackend):
    """Backend for web scraping with rate limiting and robots.txt compliance."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "webscraper"
    
    @classmethod
    def get_description(cls) -> str:
        return "Scrape and parse web content with rate limiting and robots.txt compliance"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "beautifulsoup4>=4.12.0",
            "requests>=2.28.0",
            "httpx>=0.24.0",
            "selenium>=4.0.0",
            "playwright>=1.30.0",
            "lxml>=4.9.0",
            "urllib3>=1.26.0",
            "aiohttp>=3.8.0",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "scrape_url",
                "description": "Scrape content from a web page with rate limiting and robots.txt compliance",
                "parameters": "url: str, method: str = 'requests', extract_text: bool = True, extract_links: bool = False, css_selector: str = None",
                "return_type": "dict",
                "implementation": '''logger.info(f"Scraping URL: {url}")

# Validate URL
if not await _validate_url(url):
    raise ValueError(f"Invalid or disallowed URL: {url}")

# Check robots.txt compliance
if RESPECT_ROBOTS_TXT and not await _check_robots_txt(url):
    return {
        "success": False,
        "error": "Access denied by robots.txt",
        "url": url
    }
    
# Check rate limiting
if not await _check_rate_limit(url):
    return {
        "success": False,
        "error": "Rate limit exceeded for this domain",
        "url": url
    }

# Record request for rate limiting
await _record_request(url)

# Choose scraping method
if method == "selenium":
    content_data = await _scrape_with_selenium(url, css_selector)
elif method == "playwright":
    content_data = await _scrape_with_playwright(url, css_selector)
else:  # default to requests
    content_data = await _scrape_with_requests(url, css_selector)
    
if not content_data["success"]:
    return content_data

# Parse content
soup = BeautifulSoup(content_data["html"], 'html.parser')

# Extract metadata
metadata = await _extract_metadata(soup)

# Extract text content if requested
text_content = ""
if extract_text:
    text_content = await _extract_clean_text(soup)

# Extract links if requested
links = []
if extract_links:
    links = await _extract_links(soup, url)

# Apply CSS selector if provided
selected_content = ""
if css_selector:
    selected_elements = soup.select(css_selector)
    if selected_elements:
        if extract_text:
            selected_content = "\\n".join([elem.get_text(strip=True) for elem in selected_elements])
        else:
            selected_content = "\\n".join([str(elem) for elem in selected_elements])
    
return {
    "success": True,
    "url": url,
    "title": metadata.get("title", ""),
    "description": metadata.get("description", ""),
    "text_content": text_content if extract_text else "",
    "html_content": content_data["html"] if not extract_text else "",
    "selected_content": selected_content,
    "links": links if extract_links else [],
    "metadata": metadata,
    "method": method,
    "status_code": content_data.get("status_code", 200),
    "response_time": content_data.get("response_time", 0),
    "content_length": len(content_data["html"]),
    "timestamp": datetime.now().isoformat()
}'''
            },
            {
                "name": "extract_links",
                "description": "Extract all links from a web page",
                "parameters": "url: str, filter_domain: bool = False, include_external: bool = True",
                "return_type": "dict",
                "implementation": '''logger.info(f"Extracting links from: {url}")

# Validate URL first
if not await _validate_url(url):
    return {
        "success": False,
        "error": f"Invalid or disallowed URL: {url}",
        "url": url
    }

# Check rate limiting
if not await _check_rate_limit(url):
    return {
        "success": False,
        "error": "Rate limit exceeded for this domain",
        "url": url
    }

# Record request for rate limiting
await _record_request(url)

# Scrape the page
async with get_http_client() as client:
    response = await client.get(url)
    if response.status_code != 200:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.reason_phrase}",
            "url": url
        }

# Parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Extract all links
links = []
base_domain = urlparse(url).netloc

for link_elem in soup.find_all('a', href=True):
    href = link_elem['href']
    text = link_elem.get_text(strip=True)
    
    # Convert relative URLs to absolute
    absolute_url = urljoin(url, href)
    link_domain = urlparse(absolute_url).netloc
    
    # Apply domain filtering
    if filter_domain and link_domain != base_domain:
        continue
    
    if not include_external and link_domain != base_domain:
        continue
    
    # Extract additional attributes
    link_info = {
        "url": absolute_url,
        "text": text,
        "title": link_elem.get('title', ''),
        "domain": link_domain,
        "is_external": link_domain != base_domain,
        "rel": link_elem.get('rel', []),
        "target": link_elem.get('target', '')
    }
    
    links.append(link_info)

# Remove duplicates while preserving order
seen_urls = set()
unique_links = []
for link in links:
    if link["url"] not in seen_urls:
        seen_urls.add(link["url"])
        unique_links.append(link)

# Categorize links
internal_links = [link for link in unique_links if not link["is_external"]]
external_links = [link for link in unique_links if link["is_external"]]

return {
    "success": True,
    "url": url,
    "links": unique_links,
    "internal_links": internal_links,
    "external_links": external_links,
    "total_links": len(unique_links),
    "internal_count": len(internal_links),
    "external_count": len(external_links),
    "base_domain": base_domain
    }
'''
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of a web page using browser automation",
                "parameters": "url: str, width: int = 1920, height: int = 1080, full_page: bool = False, format: str = 'png'",
                "return_type": "dict",
                "implementation": '''logger.info(f"Taking screenshot of: {url}")
    
    # Validate URL
    if not await _validate_url(url):
        raise ValueError(f"Invalid or disallowed URL: {url}")
    
    # Check rate limiting
    if not await _check_rate_limit(url):
        return {
            "success": False,
            "error": "Rate limit exceeded for this domain",
            "url": url
        }
    
    # Record request for rate limiting
    await _record_request(url)
    
    # Take screenshot using preferred method
    if SCREENSHOT_METHOD == "playwright":
        screenshot_data = await _screenshot_with_playwright(url, width, height, full_page, format)
    else:  # selenium
        screenshot_data = await _screenshot_with_selenium(url, width, height, full_page, format)
    
    if screenshot_data["success"]:
        # Encode screenshot as base64
        import base64
        screenshot_base64 = base64.b64encode(screenshot_data["image_data"]).decode('utf-8')
        
        return {
            "success": True,
            "url": url,
            "screenshot_base64": screenshot_base64,
            "format": format,
            "width": width,
            "height": height,
            "full_page": full_page,
            "file_size": len(screenshot_data["image_data"]),
            "method": SCREENSHOT_METHOD
        }
    else:
        return screenshot_data
'''
            },
            {
                "name": "check_robots_txt",
                "description": "Check robots.txt file for a domain and verify access permissions",
                "parameters": "url: str, user_agent: str = '*'",
                "return_type": "dict",
                "implementation": '''logger.info(f"Checking robots.txt for: {url}")
    
    # Parse domain from URL
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    # Fetch robots.txt
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(robots_url, headers={"User-Agent": USER_AGENT})
            robots_content = response.text if response.status_code == 200 else ""
        except Exception:
            robots_content = ""
    
    # Parse robots.txt
    from urllib.robotparser import RobotFileParser
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    
    if robots_content:
        rp.feed(robots_content)
    
    # Check if URL is allowed
    can_fetch = rp.can_fetch(user_agent, url)
    
    # Extract relevant directives
    directives = []
    if robots_content:
        lines = robots_content.split('\\n')
        current_ua = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('User-agent:'):
                current_ua = line.split(':', 1)[1].strip()
            elif line.startswith(('Disallow:', 'Allow:', 'Crawl-delay:', 'Sitemap:')):
                directives.append({
                    "user_agent": current_ua,
                    "directive": line
                })
    
    return {
        "success": True,
        "url": url,
        "robots_url": robots_url,
        "can_fetch": can_fetch,
        "user_agent": user_agent,
        "robots_exists": bool(robots_content),
        "robots_content": robots_content,
        "directives": directives,
        "domain": parsed_url.netloc
    }
'''
            },
            {
                "name": "get_page_info",
                "description": "Get comprehensive information about a web page without full content",
                "parameters": "url: str",
                "return_type": "dict",
                "implementation": '''logger.info(f"Getting page info for: {url}")
    
    # Validate URL
    if not await _validate_url(url):
        raise ValueError(f"Invalid or disallowed URL: {url}")
    
    # Check rate limiting
    if not await _check_rate_limit(url):
        return {
            "success": False,
            "error": "Rate limit exceeded for this domain",
            "url": url
        }
    
    # Record request for rate limiting
    await _record_request(url)
    
    # Fetch page headers first
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        # HEAD request first to get basic info
        head_response = await client.head(url, headers={"User-Agent": USER_AGENT})
        
        # GET request for content analysis
        start_time = time.time()
        response = await client.get(url, headers={"User-Agent": USER_AGENT})
        response_time = (time.time() - start_time) * 1000
    
    # Parse HTML for metadata
    soup = BeautifulSoup(response.text, 'html.parser')
    metadata = await _extract_metadata(soup)
    
    # Analyze page structure
    structure = {
        "total_links": len(soup.find_all('a', href=True)),
        "images": len(soup.find_all('img')),
        "forms": len(soup.find_all('form')),
        "scripts": len(soup.find_all('script')),
        "stylesheets": len(soup.find_all('link', rel='stylesheet')),
        "headings": {
            f"h{i}": len(soup.find_all(f'h{i}'))
            for i in range(1, 7)
        }
    }
    
    return {
        "success": True,
        "url": url,
        "final_url": str(response.url),
        "status_code": response.status_code,
        "response_time_ms": round(response_time, 2),
        "content_type": response.headers.get('content-type', ''),
        "content_length": len(response.content),
        "encoding": response.encoding,
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "metadata": metadata,
        "structure": structure,
        "headers": dict(response.headers),
        "redirects": len(response.history) if hasattr(response, 'history') else 0
    }
'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_scraper_config",
                "uri": "scraper://config",
                "description": "Web scraper configuration and settings",
                "parameters": "",
                "implementation": '''
    config_info = {
        "user_agent": USER_AGENT,
        "respect_robots_txt": RESPECT_ROBOTS_TXT,
        "rate_limit_delay": RATE_LIMIT_DELAY,
        "request_timeout": REQUEST_TIMEOUT,
        "allowed_domains": ALLOWED_DOMAINS if ALLOWED_DOMAINS else "all",
        "blocked_domains": BLOCKED_DOMAINS,
        "screenshot_method": SCREENSHOT_METHOD,
        "max_content_length": MAX_CONTENT_LENGTH
    }
    
    return json.dumps(config_info, indent=2)
'''
            },
            {
                "name": "get_domain_info",
                "uri": "scraper://domain/{domain}",
                "description": "Information about scraping activity for a specific domain",
                "parameters": "domain: str",
                "implementation": '''
    domain_stats = await _get_domain_stats(domain)
    
    return json.dumps({
        "domain": domain,
        "requests_made": domain_stats.get("requests", 0),
        "last_request": domain_stats.get("last_request", "never"),
        "rate_limit_remaining": await _get_rate_limit_remaining(domain),
        "robots_txt_checked": domain_stats.get("robots_checked", False),
        "robots_txt_allows": domain_stats.get("robots_allows", True)
    }, indent=2)
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "import time",
            "import asyncio",
            "from datetime import datetime, timedelta",
            "from urllib.parse import urljoin, urlparse, quote",
            "from typing import Dict, List, Any, Optional",
            "import httpx",
            "import requests",
            "from bs4 import BeautifulSoup",
            "import os",
            "import re",
            "import base64",
            "from urllib.robotparser import RobotFileParser",
        ]
    
    def get_init_code(self) -> str:
        user_agent = self.config.parameters.get("user_agent", "MCP-Scraper/1.0")
        respect_robots = self.config.parameters.get("respect_robots_txt", True)
        rate_limit_delay = self.config.parameters.get("rate_limit_delay", 1.0)
        timeout = self.config.parameters.get("request_timeout", 30)
        allowed_domains = self.config.parameters.get("allowed_domains", [])
        blocked_domains = self.config.parameters.get("blocked_domains", [])
        
        return f'''
# Web Scraper Configuration
USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "{user_agent}")
RESPECT_ROBOTS_TXT = {respect_robots}
RATE_LIMIT_DELAY = {rate_limit_delay}  # seconds between requests to same domain
REQUEST_TIMEOUT = {timeout}
MAX_CONTENT_LENGTH = 10485760  # 10MB
SCREENSHOT_METHOD = os.getenv("SCREENSHOT_METHOD", "selenium")  # selenium or playwright

# Domain filtering
ALLOWED_DOMAINS = {allowed_domains or []}
BLOCKED_DOMAINS = {blocked_domains or []}

# Rate limiting storage
domain_request_history = {{}}
robots_cache = {{}}

async def _validate_url(url: str) -> bool:
    """Validate URL and check domain restrictions."""
    try:
        parsed = urlparse(url)
        
        # Basic URL validation
        if not parsed.scheme or not parsed.netloc:
            return False
        
        if parsed.scheme not in ['http', 'https']:
            return False
        
        domain = parsed.netloc.lower()
        
        # Check blocked domains
        for blocked in BLOCKED_DOMAINS:
            if blocked.lower() in domain:
                logger.warning(f"Domain blocked: {{domain}}")
                return False
        
        # Check allowed domains (if specified)
        if ALLOWED_DOMAINS:
            allowed = any(allowed_domain.lower() in domain for allowed_domain in ALLOWED_DOMAINS)
            if not allowed:
                logger.warning(f"Domain not in allowed list: {{domain}}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"URL validation error: {{e}}")
        return False

async def _check_robots_txt(url: str) -> bool:
    """Check if URL is allowed by robots.txt."""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check cache first
        if domain in robots_cache:
            rp = robots_cache[domain]
        else:
            # Fetch and parse robots.txt
            robots_url = f"{{parsed_url.scheme}}://{{domain}}/robots.txt"
            
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(robots_url, headers={{"User-Agent": USER_AGENT}})
                    robots_content = response.text if response.status_code == 200 else ""
            except Exception:
                # If robots.txt is inaccessible, assume allowed
                return True
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            if robots_content:
                rp.feed(robots_content)
            
            # Cache the result
            robots_cache[domain] = rp
        
        # Check if URL is allowed
        return rp.can_fetch(USER_AGENT, url)
        
    except Exception as e:
        logger.warning(f"Robots.txt check failed for {{url}}: {{e}}")
        return True  # Default to allowed if check fails

async def _check_rate_limit(url: str) -> bool:
    """Check if request is within rate limits for domain."""
    try:
        domain = urlparse(url).netloc
        current_time = time.time()
        
        # Check last request time for this domain
        if domain in domain_request_history:
            last_request = domain_request_history[domain][-1] if domain_request_history[domain] else 0
            time_since_last = current_time - last_request
            
            if time_since_last < RATE_LIMIT_DELAY:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check error: {{e}}")
        return True

async def _record_request(url: str) -> None:
    """Record request timestamp for rate limiting."""
    try:
        domain = urlparse(url).netloc
        current_time = time.time()
        
        if domain not in domain_request_history:
            domain_request_history[domain] = []
        
        # Add current request
        domain_request_history[domain].append(current_time)
        
        # Clean old requests (keep last 100)
        if len(domain_request_history[domain]) > 100:
            domain_request_history[domain] = domain_request_history[domain][-100:]
        
    except Exception as e:
        logger.error(f"Request recording error: {{e}}")

async def _scrape_with_requests(url: str, css_selector: str = None) -> Dict[str, Any]:
    """Scrape using requests library."""
    try:
        start_time = time.time()
        
        response = requests.get(
            url,
            headers={{"User-Agent": USER_AGENT}},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Check content length
        if len(response.content) > MAX_CONTENT_LENGTH:
            return {{
                "success": False,
                "error": f"Content too large: {{len(response.content)}} bytes"
            }}
        
        return {{
            "success": True,
            "html": response.text,
            "status_code": response.status_code,
            "response_time": response_time
        }}
        
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}

async def _scrape_with_selenium(url: str, css_selector: str = None) -> Dict[str, Any]:
    """Scrape using Selenium WebDriver."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={{USER_AGENT}}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            start_time = time.time()
            driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            html = driver.page_source
            response_time = (time.time() - start_time) * 1000
            
            return {{
                "success": True,
                "html": html,
                "status_code": 200,
                "response_time": response_time
            }}
            
        finally:
            driver.quit()
            
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}

async def _scrape_with_playwright(url: str, css_selector: str = None) -> Dict[str, Any]:
    """Scrape using Playwright."""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=USER_AGENT)
            
            start_time = time.time()
            await page.goto(url, wait_until="networkidle")
            
            html = await page.content()
            response_time = (time.time() - start_time) * 1000
            
            await browser.close()
            
            return {{
                "success": True,
                "html": html,
                "status_code": 200,
                "response_time": response_time
            }}
            
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}

async def _extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract metadata from HTML."""
    metadata = {{}}
    
    # Title
    title_tag = soup.find('title')
    metadata['title'] = title_tag.get_text(strip=True) if title_tag else ""
    
    # Meta tags
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
        content = meta.get('content')
        
        if name and content:
            metadata[name.lower()] = content
    
    # OpenGraph tags
    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    for tag in og_tags:
        property_name = tag.get('property', '').replace('og:', '')
        content = tag.get('content', '')
        if property_name and content:
            metadata[f'og_{{property_name}}'] = content
    
    # Twitter card tags
    twitter_tags = soup.find_all('meta', attrs={{'name': lambda x: x and x.startswith('twitter:')}})
    for tag in twitter_tags:
        name = tag.get('name', '').replace('twitter:', '')
        content = tag.get('content', '')
        if name and content:
            metadata[f'twitter_{{name}}'] = content
    
    return metadata

async def _extract_clean_text(soup: BeautifulSoup) -> str:
    """Extract clean text content from HTML."""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\\n'.join(chunk for chunk in chunks if chunk)
    
    return text

async def _extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
    """Extract all links from HTML."""
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)
        
        # Convert relative URLs to absolute
        absolute_url = urljoin(base_url, href)
        
        links.append({{
            "url": absolute_url,
            "text": text,
            "title": link.get('title', ''),
            "rel": link.get('rel', [])
        }})
    
    return links

async def _screenshot_with_selenium(url: str, width: int, height: int, full_page: bool, format: str) -> Dict[str, Any]:
    """Take screenshot using Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={{width}},{{height}}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            if full_page:
                # Get full page height
                total_height = driver.execute_script("return document.body.scrollHeight")
                driver.set_window_size(width, total_height)
            
            screenshot_data = driver.get_screenshot_as_png()
            
            return {{
                "success": True,
                "image_data": screenshot_data
            }}
            
        finally:
            driver.quit()
            
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}

async def _screenshot_with_playwright(url: str, width: int, height: int, full_page: bool, format: str) -> Dict[str, Any]:
    """Take screenshot using Playwright."""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={{"width": width, "height": height}})
            
            await page.goto(url, wait_until="networkidle")
            
            screenshot_data = await page.screenshot(full_page=full_page, type=format)
            
            await browser.close()
            
            return {{
                "success": True,
                "image_data": screenshot_data
            }}
            
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}

async def _get_domain_stats(domain: str) -> Dict[str, Any]:
    """Get statistics for a domain."""
    stats = {{
        "requests": len(domain_request_history.get(domain, [])),
        "last_request": "never",
        "robots_checked": domain in robots_cache,
        "robots_allows": True
    }}
    
    if domain in domain_request_history and domain_request_history[domain]:
        last_request_time = domain_request_history[domain][-1]
        stats["last_request"] = datetime.fromtimestamp(last_request_time).isoformat()
    
    if domain in robots_cache:
        # This is a simplified check - in practice, you'd want to check specific URLs
        stats["robots_allows"] = True  # Placeholder
    
    return stats

async def _get_rate_limit_remaining(domain: str) -> float:
    """Get remaining time before next request is allowed."""
    if domain not in domain_request_history or not domain_request_history[domain]:
        return 0.0
    
    last_request = domain_request_history[domain][-1]
    current_time = time.time()
    elapsed = current_time - last_request
    
    return max(0.0, RATE_LIMIT_DELAY - elapsed)
'''
    
    def get_cleanup_code(self) -> str:
        return '''
        # Cleanup web scraper resources
        logger.info("Cleaning up web scraper resources...")
        # Close any remaining browser instances would be handled by context managers
'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Validate rate limit delay
        rate_limit_delay = self.config.parameters.get("rate_limit_delay", 1.0)
        if not isinstance(rate_limit_delay, (int, float)) or rate_limit_delay < 0:
            errors.append("rate_limit_delay must be a non-negative number")
        
        # Validate timeout
        timeout = self.config.parameters.get("request_timeout", 30)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            errors.append("request_timeout must be an integer between 1 and 300 seconds")
        
        # Validate user agent
        user_agent = self.config.parameters.get("user_agent", "")
        if not user_agent or len(user_agent) < 10:
            errors.append("user_agent must be a descriptive string (at least 10 characters)")
        
        # Validate domains
        allowed_domains = self.config.parameters.get("allowed_domains", [])
        if allowed_domains and not isinstance(allowed_domains, list):
            errors.append("allowed_domains must be a list of domain names")
        
        blocked_domains = self.config.parameters.get("blocked_domains", [])
        if blocked_domains and not isinstance(blocked_domains, list):
            errors.append("blocked_domains must be a list of domain names")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "SCRAPER_USER_AGENT": "User agent string for web requests",
            "SCREENSHOT_METHOD": "Screenshot method: selenium or playwright",
            "SCRAPER_RATE_LIMIT": "Rate limit delay in seconds between requests",
            "SCRAPER_TIMEOUT": "Request timeout in seconds",
            "SCRAPER_ALLOWED_DOMAINS": "Comma-separated list of allowed domains",
            "SCRAPER_BLOCKED_DOMAINS": "Comma-separated list of blocked domains",
        }
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text",
                "message": "Enter a description for your web scraper MCP server:",
                "default": "MCP server with web scraper backend",
            },
            {
                "name": "user_agent",
                "type": "text",
                "message": "Enter User-Agent string for web requests:",
                "default": "MCP-WebScraper/1.0 (Responsible Scraping Bot)",
                "required": True,
            },
            {
                "name": "respect_robots_txt",
                "type": "bool",
                "message": "Respect robots.txt files?",
                "default": True,
            },
            {
                "name": "rate_limit_delay",
                "type": "int",
                "message": "Enter delay between requests to same domain (seconds):",
                "default": 1,
            },
            {
                "name": "request_timeout",
                "type": "int",
                "message": "Enter request timeout (seconds):",
                "default": 30,
            },
            {
                "name": "allowed_domains",
                "type": "text",
                "message": "Enter allowed domains (comma-separated, empty for all):",
                "default": "",
            },
            {
                "name": "blocked_domains",
                "type": "text",
                "message": "Enter blocked domains (comma-separated):",
                "default": "",
            },
        ]