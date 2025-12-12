# Contributing Guide

Thank you for your interest in contributing to the Workflow Engine! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd workflow-engine
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies** (optional)
```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
workflow-engine/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── engine.py            # Workflow engine core
│   ├── models.py            # Pydantic models
│   ├── tools.py             # Tool registry and implementations
│   ├── database.py          # Database operations
│   └── workflows/
│       ├── __init__.py
│       └── code_review.py   # Example workflow
├── tests/                   # Test files (to be added)
├── docs/                    # Additional documentation
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md               # Main documentation
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Formatting

Use Black for automatic formatting:
```bash
black app/
```

### Linting

Use flake8 for linting:
```bash
flake8 app/ --max-line-length=88 --extend-ignore=E203
```

### Type Checking

Use mypy for type checking:
```bash
mypy app/ --ignore-missing-imports
```

## Adding New Features

### 1. Adding a New Tool

Create a new tool function in `app/tools.py`:

```python
def my_new_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Brief description of what the tool does.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with new fields
    """
    # Your implementation here
    result = process_state(state)
    state["new_field"] = result
    return state

# Register the tool
tool_registry.register("my_new_tool", my_new_tool)
```

**Tool Guidelines:**
- Pure functions (no side effects)
- Clear input/output contracts
- Comprehensive docstrings
- Error handling
- Type hints

### 2. Adding a New Workflow

Create a new file in `app/workflows/`:

```python
# app/workflows/my_workflow.py

def get_my_workflow_definition():
    """Returns the graph definition for my workflow"""
    return {
        "name": "my_workflow",
        "nodes": {
            "step1": {"tool": "tool1", "next": "step2"},
            "step2": {"tool": "tool2", "next": "end"}
        },
        "start_node": "step1"
    }
```

### 3. Adding API Endpoints

Add new endpoints in `app/main.py`:

```python
@app.get("/my-endpoint")
async def my_endpoint():
    """
    Endpoint description.
    
    Returns:
        Response data
    """
    # Implementation
    return {"data": "value"}
```

**Endpoint Guidelines:**
- RESTful design
- Proper HTTP methods
- Clear documentation
- Error handling
- Input validation

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_engine.py

# Run with verbose output
pytest -v
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_tools.py

import pytest
from app.tools import extract_functions

def test_extract_functions():
    """Test function extraction"""
    state = {
        "code": "def test():\n    pass"
    }
    result = extract_functions(state)
    
    assert "functions" in result
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "test"

def test_extract_functions_syntax_error():
    """Test handling of syntax errors"""
    state = {
        "code": "def test(\n    pass"  # Invalid syntax
    }
    result = extract_functions(state)
    
    assert "functions" in result
    assert "error" in result["functions"][0]
```

**Testing Guidelines:**
- Test happy paths and edge cases
- Use descriptive test names
- One assertion per test (when possible)
- Use fixtures for common setup
- Mock external dependencies

### Test Coverage Goals

- **Overall**: >80%
- **Core engine**: >90%
- **Tools**: >85%
- **API endpoints**: >75%

## Documentation

### Code Documentation

Use docstrings for all public functions and classes:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> my_function("test", 42)
        True
    """
    # Implementation
```

### API Documentation

FastAPI automatically generates documentation from:
- Endpoint docstrings
- Pydantic models
- Type hints
- Response models

Ensure all endpoints have:
- Clear descriptions
- Request/response examples
- Error responses documented

### README Updates

When adding features, update:
- Feature list
- API endpoints section
- Examples
- Configuration options

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions

### Commit Messages

Follow conventional commits:

```
type(scope): brief description

Longer description if needed.

- Bullet points for details
- Multiple changes

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(tools): add sentiment analysis tool

Add new tool for analyzing text sentiment using rule-based approach.

- Supports positive/negative/neutral classification
- Returns confidence scores
- Handles edge cases

Closes #45
```

### Pull Request Process

1. **Create a branch**
```bash
git checkout -b feature/my-feature
```

2. **Make changes and commit**
```bash
git add .
git commit -m "feat: add my feature"
```

3. **Push to remote**
```bash
git push origin feature/my-feature
```

4. **Create Pull Request**
- Clear title and description
- Reference related issues
- Add screenshots if UI changes
- Request reviews

5. **Address feedback**
- Make requested changes
- Push updates
- Re-request review

6. **Merge**
- Squash commits if needed
- Delete branch after merge

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Focus on code, not the person
- Explain reasoning
- Suggest alternatives
- Approve when satisfied

### As an Author

- Respond to all comments
- Ask for clarification
- Make requested changes
- Thank reviewers

## Performance Considerations

### Optimization Guidelines

1. **Database Queries**
   - Use indexes
   - Batch operations
   - Avoid N+1 queries

2. **API Endpoints**
   - Use async/await
   - Implement caching
   - Paginate large results

3. **Workflow Execution**
   - Minimize state size
   - Optimize tool functions
   - Use parallel execution when possible

### Profiling

```python
# Profile a function
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Security

### Security Checklist

- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Authentication
- [ ] Authorization
- [ ] Secure dependencies

### Reporting Security Issues

**Do not** open public issues for security vulnerabilities.

Instead:
1. Email security@example.com
2. Include detailed description
3. Provide reproduction steps
4. Wait for response before disclosure

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. Update version in `app/__init__.py`
2. Update CHANGELOG.md
3. Run all tests
4. Update documentation
5. Create git tag
6. Build Docker image
7. Deploy to staging
8. Test in staging
9. Deploy to production
10. Announce release

## Getting Help

### Resources

- **Documentation**: README.md, API_REFERENCE.md
- **Examples**: example_usage.py
- **Architecture**: ARCHITECTURE.md
- **API Docs**: http://localhost:8000/docs

### Communication

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: dev@example.com

### Common Issues

**Import errors**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Database locked**
```bash
# Remove database and restart
rm workflow_engine.db
```

**Port in use**
```bash
# Use different port
uvicorn app.main:app --port 8001
```

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

If you have questions not covered here:
1. Check existing documentation
2. Search closed issues
3. Open a new issue with the "question" label

Thank you for contributing! 🎉
