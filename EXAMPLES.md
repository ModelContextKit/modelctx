# MCP Quick Setup Tool - Examples

> Real-world examples demonstrating the capabilities of the MCP Quick Setup Tool

## Overview

This directory contains example projects that showcase how to use the MCP Quick Setup Tool to create various types of MCP servers. Each example includes complete source code, configuration, and documentation.

## Available Examples

### 🗄️ Database Examples

#### 1. **E-commerce Inventory Manager** (`ecommerce-inventory/`)
- **Backend**: Database (PostgreSQL)
- **Use Case**: Manage product inventory for an e-commerce platform
- **Features**: Product queries, stock management, sales analytics
- **Tools**: `get_products`, `update_stock`, `get_sales_report`, `low_stock_alert`

#### 2. **Employee Directory** (`employee-directory/`)
- **Backend**: Database (MySQL)  
- **Use Case**: Company employee management system
- **Features**: Employee lookup, department management, reporting
- **Tools**: `find_employee`, `list_departments`, `get_org_chart`

### 🌐 API Examples

#### 3. **Weather Service Integration** (`weather-service/`)
- **Backend**: REST API
- **Use Case**: Weather data integration with OpenWeatherMap API
- **Features**: Current weather, forecasts, weather alerts
- **Tools**: `get_current_weather`, `get_forecast`, `get_weather_alerts`

#### 4. **GitHub Repository Manager** (`github-manager/`)
- **Backend**: REST API
- **Use Case**: GitHub repository management and analytics
- **Features**: Repository info, commit history, issue tracking
- **Tools**: `get_repo_info`, `list_commits`, `create_issue`, `get_pull_requests`

### 📁 Filesystem Examples

#### 5. **Document Management System** (`document-manager/`)
- **Backend**: Filesystem
- **Use Case**: Manage and search through document collections
- **Features**: Document indexing, full-text search, metadata extraction
- **Tools**: `index_documents`, `search_content`, `get_document_info`

#### 6. **Log File Analyzer** (`log-analyzer/`)
- **Backend**: Filesystem
- **Use Case**: Analyze application log files for insights
- **Features**: Error detection, performance metrics, trend analysis
- **Tools**: `analyze_errors`, `get_performance_metrics`, `generate_report`

### 🕷️ Web Scraping Examples

#### 7. **News Aggregator** (`news-aggregator/`)
- **Backend**: Web Scraper
- **Use Case**: Aggregate news articles from multiple sources
- **Features**: Article extraction, categorization, sentiment analysis
- **Tools**: `scrape_articles`, `categorize_news`, `get_trending_topics`

#### 8. **Product Price Monitor** (`price-monitor/`)
- **Backend**: Web Scraper
- **Use Case**: Monitor product prices across e-commerce sites
- **Features**: Price tracking, alerts, historical data
- **Tools**: `track_price`, `price_alert`, `get_price_history`

## Quick Start

Each example can be generated using the MCP Quick Setup Tool:

```bash
# Generate an example project
mcp-setup create weather-service --backend api

# Or use the interactive wizard
mcp-setup wizard
# Then follow the prompts and select the desired backend type
```

## Example Usage

### 1. E-commerce Inventory Manager

```bash
# Generate the project
mcp-setup create ecommerce-inventory --backend database

# Configure the database
cd ecommerce-inventory
cp .env.template .env
# Edit .env with your PostgreSQL connection details

# Run the server
python server.py

# Test with Claude Desktop or MCP Inspector
npx @modelcontextprotocol/inspector python server.py
```

**Sample Interactions**:
```
Human: Can you check our current stock levels for electronics?

Claude: I'll check the current stock levels for electronics products using the inventory system.

[Uses get_products tool with category filter]

Based on the inventory data, here are the current stock levels for electronics:

- iPhone 15 Pro: 45 units in stock
- MacBook Air M2: 23 units in stock  
- AirPods Pro: 67 units in stock
- iPad Air: 12 units in stock (Low Stock Alert!)

The iPad Air is running low and may need restocking soon.
```

### 2. Weather Service Integration

```bash
# Generate the project
mcp-setup create weather-service --backend api

# Configure the API
cd weather-service
cp .env.template .env
# Add your OpenWeatherMap API key to .env

# Run the server
python server.py
```

**Sample Interactions**:
```
Human: What's the weather like in San Francisco today?

Claude: I'll get the current weather conditions for San Francisco.

[Uses get_current_weather tool]

Current weather in San Francisco:
- Temperature: 68°F (20°C)
- Conditions: Partly cloudy
- Humidity: 72%
- Wind: 8 mph from the west
- Visibility: 10 miles

It's a pleasant day with partly cloudy skies!
```

### 3. Document Management System

```bash
# Generate the project
mcp-setup create document-manager --backend filesystem

# Configure allowed paths
cd document-manager
cp .env.template .env
# Set FS_ALLOWED_PATHS to your document directories

# Run the server
python server.py
```

**Sample Interactions**:
```
Human: Find all documents related to "quarterly reports" from last year

Claude: I'll search through your document collection for quarterly reports from last year.

[Uses search_content tool with filters]

Found 8 documents related to quarterly reports:

1. Q1_2023_Financial_Report.pdf (March 2023)
2. Q2_2023_Sales_Report.docx (June 2023)
3. Q3_2023_Marketing_Analysis.pdf (September 2023)
4. Q4_2023_Year_End_Summary.pdf (December 2023)

Would you like me to extract specific information from any of these reports?
```

## Configuration Examples

Each example includes complete configuration for different scenarios:

### Development Configuration
```yaml
# config/config.yaml
server:
  name: "weather-service"
  description: "Weather data integration service"

backend:
  type: "api"
  base_url: "https://api.openweathermap.org/data/2.5"
  rate_limit: 60
  timeout: 10

logging:
  level: "DEBUG"
  
security:
  validate_inputs: true
  log_requests: true
```

### Production Configuration
```yaml
# config/config.yaml  
server:
  name: "weather-service"
  description: "Weather data integration service"

backend:
  type: "api"
  base_url: "https://api.openweathermap.org/data/2.5"
  rate_limit: 1000
  timeout: 30

logging:
  level: "INFO"
  file: "/var/log/weather-service.log"
  
security:
  validate_inputs: true
  log_requests: false
  audit_log: "/var/log/weather-service-audit.log"
```

## Testing Examples

Each example includes comprehensive tests:

```bash
# Run all tests
cd ecommerce-inventory
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_inventory.py -v
python -m pytest tests/test_security.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

## Deployment Examples

### Docker Deployment
```bash
# Build and run with Docker
cd weather-service
docker build -t weather-service .
docker run -d --name weather-service \
  --env-file .env \
  weather-service
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
kubectl get pods -l app=weather-service
```

### Cloud Deployment
```bash
# Deploy to AWS with Terraform
cd terraform/
terraform init
terraform plan
terraform apply
```

## Integration Examples

### Claude Desktop Integration

Each example includes Claude Desktop configuration:

```json
{
  "mcpServers": {
    "weather-service": {
      "command": "python",
      "args": ["/path/to/weather-service/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your-api-key",
        "LOG_LEVEL": "INFO"
      }
    },
    "document-manager": {
      "command": "python", 
      "args": ["/path/to/document-manager/server.py"],
      "env": {
        "FS_ALLOWED_PATHS": "/home/user/Documents,/home/user/Projects"
      }
    }
  }
}
```

### Custom Tool Integration

Examples of extending the generated servers with custom tools:

```python
# Adding a custom tool to the weather service
@mcp.tool()
async def get_weather_recommendation(location: str, activity: str) -> dict:
    """Get weather-based activity recommendations."""
    weather = await get_current_weather(location)
    
    if activity == "outdoor_sports":
        if weather["temperature"] > 50 and weather["precipitation"] < 0.1:
            return {"recommendation": "Great weather for outdoor sports!"}
        else:
            return {"recommendation": "Consider indoor activities today."}
    
    # Add more activity-specific recommendations
    return {"recommendation": "Check current conditions"}
```

## Performance Examples

### Benchmarking
```bash
# Benchmark the API backend
cd weather-service
python benchmark.py --requests 1000 --concurrent 10

# Results:
# Average response time: 245ms
# Requests per second: 38
# Success rate: 99.8%
```

### Optimization Examples
```python
# Connection pooling optimization
async with httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
    timeout=httpx.Timeout(30.0)
) as client:
    # Reuse connections for better performance
    pass

# Caching optimization  
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_weather_data(location: str, timestamp: int) -> dict:
    # Cache weather data for 5 minutes
    pass
```

## Security Examples

### Input Validation
```python
# Example of comprehensive input validation
from pydantic import BaseModel, validator

class WeatherRequest(BaseModel):
    location: str
    units: str = "metric"
    
    @validator('location')
    def validate_location(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Location must be 2-100 characters')
        return v.strip()
    
    @validator('units')
    def validate_units(cls, v):
        if v not in ['metric', 'imperial', 'kelvin']:
            raise ValueError('Units must be metric, imperial, or kelvin')
        return v
```

### Rate Limiting
```python
# Advanced rate limiting example
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        requests = self.requests[client_id]
        
        # Remove old requests
        requests[:] = [req_time for req_time in requests 
                      if now - req_time < self.window_seconds]
        
        if len(requests) >= self.max_requests:
            return False
        
        requests.append(now)
        return True
```

## Contributing

We welcome contributions to the examples! To add a new example:

1. Create a new directory under `examples/`
2. Include complete source code and configuration
3. Add comprehensive documentation
4. Include tests and deployment examples
5. Update this README with your example

## Support

For help with the examples:

- 📚 Check the individual README files in each example directory
- 🐛 [Report issues](https://github.com/ModelContextKit/modelctx/issues)
- 💬 [Join discussions](https://github.com/ModelContextKit/modelctx/discussions)
- 📧 Support: Create an issue for help

---

These examples demonstrate the power and flexibility of the MCP Quick Setup Tool. Use them as starting points for your own MCP server projects!