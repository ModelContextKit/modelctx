# Security Policy

## Supported Versions

We currently support the following versions of ModelContextKit with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Features

ModelContextKit includes several built-in security features in generated MCP servers:

### Generated Code Security

- **Input Validation**: All user inputs are validated and sanitized
- **SQL Injection Prevention**: Parameterized queries and input validation
- **Path Traversal Protection**: File system access controls and path validation  
- **Rate Limiting**: Built-in rate limiting for API and web scraping backends
- **Access Controls**: Configurable permission systems
- **Audit Logging**: Comprehensive logging of all operations
- **Secure Credential Management**: Environment variable handling for secrets

### Template Security

- **Code Injection Prevention**: Template variables are properly escaped
- **Syntax Validation**: All generated code is validated for correctness
- **Type Safety**: Proper type hints and validation
- **Error Handling**: Graceful error handling without information leakage

## Reporting a Vulnerability

We take the security of ModelContextKit seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create Public Issues

Please **do not** create public GitHub issues for security vulnerabilities, as this could put users at risk.

### 2. Contact Us Privately

Send security reports to:
- **Email**: Create a private issue on GitHub and request security contact
- **GitHub**: Use GitHub's private vulnerability reporting feature

### 3. Include Detailed Information

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: What could an attacker accomplish?
- **Reproduction**: Step-by-step instructions to reproduce
- **Generated Code**: If applicable, include the problematic generated code
- **Environment**: Python version, OS, ModelContextKit version
- **Suggested Fix**: If you have ideas for fixing the issue

### Example Report Template

```
**Vulnerability Type**: [e.g., Code Injection, Path Traversal]

**Affected Component**: [e.g., Filesystem Backend, Template Engine]

**Description**: 
[Clear description of the vulnerability]

**Steps to Reproduce**:
1. Generate server with: `modelctx create test --backend filesystem`
2. Configure with: [specific configuration]
3. Execute: [specific command or input]
4. Observe: [security issue]

**Impact**:
[What could an attacker do with this vulnerability?]

**Affected Versions**:
[Which versions are affected?]

**Suggested Mitigation**:
[If you have suggestions for fixing]
```

## Response Timeline

We aim to respond to security reports according to the following timeline:

- **Initial Response**: Within 48 hours
- **Confirmation**: Within 5 business days
- **Fix Development**: Varies by complexity
- **Release**: Critical issues within 7 days, others with next release

## Security Best Practices for Users

When using ModelContextKit and the generated MCP servers:

### Development

1. **Keep Dependencies Updated**: Regularly update ModelContextKit and generated dependencies
2. **Review Generated Code**: Inspect generated code before deployment
3. **Environment Variables**: Use environment variables for secrets, never hardcode
4. **Access Controls**: Configure appropriate access controls for your use case
5. **Testing**: Test generated servers in isolated environments first

### Production Deployment

1. **Network Security**: Deploy behind firewalls and use HTTPS
2. **Authentication**: Implement proper authentication for MCP servers
3. **Monitoring**: Monitor for unusual activity and errors
4. **Backups**: Regular backups of data and configurations
5. **Updates**: Apply security updates promptly

### Configuration Security

1. **Minimal Permissions**: Grant minimum necessary permissions
2. **Input Validation**: Enable all input validation features
3. **Rate Limiting**: Configure appropriate rate limits
4. **Audit Logging**: Enable comprehensive logging
5. **Error Handling**: Configure to avoid information leakage

## Known Security Considerations

### Generated Code

- Generated servers inherit the security characteristics of their dependencies
- Template-generated code should be reviewed before production use
- Configuration files may contain sensitive information

### File System Backend

- Restricts access to configured allowed paths
- Validates file types and sizes
- Prevents path traversal attacks
- Configurable read-only mode

### Database Backend

- Uses parameterized queries to prevent SQL injection
- Validates query types (read-only by default)
- Connection pooling with timeouts
- Input sanitization

### API Backend

- Rate limiting and request validation
- Secure credential handling
- Timeout configuration
- Response validation

### Web Scraper Backend

- Respects robots.txt files
- Rate limiting per domain
- URL validation and filtering
- Content size limits

## Security Updates

Security updates will be:

1. **Clearly Marked**: Security releases will be clearly identified
2. **Backwards Compatible**: When possible, security fixes will maintain compatibility
3. **Well Documented**: Security fixes will include clear upgrade instructions
4. **Promptly Released**: Critical security issues will be addressed quickly

## Third-Party Dependencies

ModelContextKit relies on various third-party packages. We:

- Monitor dependencies for known vulnerabilities
- Update dependencies regularly
- Provide clear dependency information in generated projects
- Recommend users keep dependencies updated

## Responsible Disclosure

We believe in responsible disclosure and will:

- Work with security researchers to address issues
- Provide credit to researchers who report issues responsibly
- Coordinate disclosure timing to protect users
- Publish security advisories for significant issues

## Questions or Concerns

If you have questions about security that don't involve reporting a vulnerability:

- Create a public GitHub issue with the `security` label
- Visit our website at [modelcontextkit.com](https://modelcontextkit.com)
- Start a discussion in GitHub Discussions

Thank you for helping keep ModelContextKit and its users secure!