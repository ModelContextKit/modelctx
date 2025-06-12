# Pull Request

## Description

Brief description of the changes in this PR.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement
- [ ] Performance improvement
- [ ] Security improvement

## Related Issues

Fixes #(issue number)
Relates to #(issue number)

## Changes Made

- [ ] Added/modified backend: [backend name]
- [ ] Updated templates
- [ ] Modified CLI commands
- [ ] Updated documentation
- [ ] Added/updated tests
- [ ] Fixed code generation issues

## Testing

### Manual Testing

- [ ] Tested code generation for affected backends
- [ ] Verified generated code compiles without errors
- [ ] Tested CLI commands work as expected
- [ ] Verified generated servers follow MCP protocol

### Automated Testing

- [ ] All existing tests pass
- [ ] Added tests for new functionality
- [ ] Generated code passes syntax validation
- [ ] Integration tests pass

### Backend-Specific Testing (if applicable)

- [ ] **Database**: Generated server connects and executes queries
- [ ] **API**: Generated server makes HTTP requests correctly
- [ ] **Filesystem**: Generated server handles file operations safely
- [ ] **Webscraper**: Generated server respects robots.txt and rate limits
- [ ] **Email**: Generated server sends/receives emails correctly
- [ ] **Cloud Storage**: Generated server interacts with cloud APIs

## Code Quality

- [ ] Code follows project style guidelines
- [ ] Code is properly documented (docstrings, comments)
- [ ] No hard-coded values or secrets
- [ ] Error handling is appropriate
- [ ] Generated code is readable and maintainable

## Breaking Changes

If this PR introduces breaking changes, describe them here:

- [ ] No breaking changes
- [ ] Breaking changes described below:

[Describe breaking changes and migration steps]

## Screenshots/Output (if applicable)

```
Include relevant command output, screenshots, or generated code examples
```

## Checklist

- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Generated Code Validation

For changes affecting code generation, please verify:

- [ ] Generated code compiles without syntax errors
- [ ] Generated code follows MCP protocol specifications
- [ ] Generated code includes proper error handling
- [ ] Generated code has appropriate security measures
- [ ] Generated tests pass

## Documentation Updates

- [ ] README.md updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] API documentation updated (if needed)
- [ ] Examples updated (if needed)

## Deployment Considerations

- [ ] No deployment considerations
- [ ] Database migrations required
- [ ] Configuration changes required
- [ ] Dependencies updated

## Additional Notes

Add any additional notes, concerns, or discussion points for reviewers.