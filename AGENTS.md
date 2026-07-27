# Development Guidelines

This document outlines the development practices and guidelines for working with the MCP server repository.

## Virtual Environments

Each project folder (like `omie`) should have its own virtual environment:

```bash
# Create virtual environment in each project folder
cd omie
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Testing

### Running Tests

Tests should be run from within each project's virtual environment using the project's pyproject.toml:

```bash
# Activate the project's virtual environment
cd omie
source .venv/bin/activate

# Run tests
python -m pytest
```

### Test Structure

When adding new tests, place them in the appropriate `tests/` directory within each project folder. Tests should:
- Be simple and focused
- Follow the existing test patterns
- Include both unit tests and integration tests where appropriate

## Error Handling Approach

For this project, we prefer a **simple and fail-fast** error handling approach:

1. **Simple**: Use straightforward error checking and handling
2. **Fail-fast**: When encountering unexpected conditions, fail immediately rather than trying to recover
3. **Clear messaging**: Provide descriptive error messages that help diagnose problems quickly
4. **Minimal complexity**: Avoid overly complex error recovery mechanisms

Example of preferred approach:
```python
# Good - Simple and fail-fast
def process_data(data):
    if not data:
        raise ValueError("Data cannot be empty")
    return transform(data)

# Avoid - Complex error recovery
def process_data(data):
    if not data:
        # Try to recover or provide default
        # Complicated logic that might mask real issues
        pass
```

## Development Workflow

1. Create and activate virtual environment for the project
2. Make changes to code
3. Run tests using the project's pyproject.toml specifications
4. **Ensure Docker images can be built successfully before completing tasks**
5. **Test that built images run correctly with: podman run --rm -i --ipc=host mcp/omie**
6. Commit changes with descriptive messages

## CI/CD Considerations

The repository structure assumes that each project can be developed and tested independently.

## Dependencies

All projects should use their respective `pyproject.toml` files for dependency management, ensuring that:
- Dependencies are clearly specified
- Development dependencies are separated from runtime dependencies  
- Version constraints are appropriate for stability