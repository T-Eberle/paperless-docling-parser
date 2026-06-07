# Contributing to paperless-docling-parser

Thank you for your interest in contributing to paperless-docling-parser! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

### Our Standards

- Be welcoming and inclusive
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Branch Protection

**Important:** The `main` and `dev` branches are protected. Direct pushing to these branches is disabled.

### Contribution Workflow

The workflow depends on your role:

#### External Contributors (Recommended for most contributors)

1. **Fork the repository** to your GitHub account
2. **Clone your fork** locally
3. **Create a feature branch** in your fork
4. **Make your changes** and commit them
5. **Push to your fork**
6. **Submit a Pull Request** from your fork to the original repository

#### Core Maintainers (Team members with write access)

1. **Clone the repository** directly (no fork needed)
2. **Create a feature branch** (e.g., `feature/your-feature` or `fix/issue-123`)
3. **Make your changes** and commit them
4. **Push your branch** to the repository
5. **Submit a Pull Request** from your branch to `main` or `dev`

### Before You Begin

1. Check if there's already an [issue](https://github.com/T-Eberle/paperless-docling-parser/issues) for what you want to work on
2. If not, create a new issue to discuss your proposed changes
3. Follow the appropriate workflow above based on your contributor type
4. Make your changes and submit a pull request

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for testing the full stack)
- Git
- A code editor (VS Code recommended)

### Setting Up Your Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/paperless-docling-parser.git
cd paperless-docling-parser
```

2. **Create a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
# Install the package in editable mode with development dependencies
pip install -e ".[dev]"
```

4. **Set up pre-commit hooks (if available):**

```bash
pre-commit install
```

### Running the Development Environment

Start the full stack with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- Docling-Serve API
- Paperless-ngx with your local plugin code

Access Paperless-ngx at `http://localhost:8000` (default credentials: admin/admin)

### Project Structure

```
paperless-docling-parser/
├── src/
│   └── paperless_ngx_docling/
│       ├── __init__.py
│       ├── converters/          # Async HTTP client for docling-serve
│       └── parsers.py           # Parser implementation
├── packages/
│   ├── core/                    # Core functionality
│   ├── docling_serve/           # Docling-serve integration
│   └── local/                   # Local processing
├── tests/                       # Test files
├── docker-compose.yaml          # Development stack
├── Dockerfile.docling_serve     # Docling-serve image
└── pyproject.toml              # Package configuration
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues reported in the issue tracker
- **Features**: Add new functionality or improve existing features
- **Documentation**: Improve README, add examples, or write tutorials
- **Tests**: Add or improve test coverage
- **Performance**: Optimize code for better performance
- **Refactoring**: Improve code quality and maintainability

### Detailed Workflow Steps

1. **Create a branch:**

For external contributors (in your fork):
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

For core maintainers (in the main repository):
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

2. **Make your changes:**
   - Write clean, readable code
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_converter.py

# Run with coverage
pytest --cov=src/paperless_ngx_docling
```

4. **Commit your changes:**

```bash
git add .
git commit -m "feat: add new feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `perf:` for performance improvements
- `chore:` for maintenance tasks

5. **Push your changes:**

For external contributors (to your fork):
```bash
git push origin feature/your-feature-name
```

For core maintainers (to the main repository):
```bash
git push origin feature/your-feature-name
```

6. **Create a Pull Request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - For external contributors: Select "compare across forks" and choose your fork's branch
   - For core maintainers: Select your branch from the dropdown
   - Fill in the PR template with details about your changes
   - Request review from maintainers

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all public functions and classes

### Code Quality Tools

We recommend using:

- **Black**: Code formatter
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Example configuration:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

### Documentation Standards

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Keep comments clear and concise
- Update README.md when adding new features

Example docstring:

```python
def parse_document(file_path: str, mode: str = "easyocr") -> dict:
    """Parse a document using the specified mode.
    
    Args:
        file_path: Path to the document file
        mode: Conversion mode (easyocr, tesseract, or granite_docling)
        
    Returns:
        Dictionary containing parsed document data
        
    Raises:
        ValueError: If the file path is invalid
        ConnectionError: If docling-serve is unreachable
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_converter.py

# Run with coverage report
pytest --cov=src/paperless_ngx_docling --cov-report=html
```

### Writing Tests

- Write tests for all new functionality
- Aim for high test coverage (>80%)
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (like docling-serve API calls)

Example test:

```python
def test_parse_pdf_success():
    """Test successful PDF parsing."""
    parser = DoclingParser()
    result = parser.parse("tests/sample_lorem_ipsum.pdf")
    assert result is not None
    assert "text" in result
```

### Integration Testing

Test the full stack with Docker Compose:

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/

# Stop services
docker-compose down
```

## Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Update documentation if needed
   - Add entry to CHANGELOG.md (if applicable)
   - Rebase on the latest main branch

2. **PR Description:**
   - Clearly describe what changes you made
   - Reference any related issues (e.g., "Fixes #123")
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process:**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, a maintainer will merge your PR

4. **After Merge:**
   - Delete your feature branch
   - Pull the latest changes from main

## Reporting Bugs

### Before Reporting

- Check if the bug has already been reported in [Issues](https://github.com/T-Eberle/paperless-docling-parser/issues)
- Try to reproduce the bug with the latest version
- Gather relevant information (logs, environment details, etc.)

### Bug Report Template

When reporting a bug, include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS and version
  - Python version
  - Docker version (if applicable)
  - Plugin version
- **Logs**: Relevant log output or error messages
- **Screenshots**: If applicable

## Suggesting Enhancements

We welcome feature suggestions! When suggesting an enhancement:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly and in detail
3. **Explain the use case** - why is this feature needed?
4. **Provide examples** of how it would work
5. **Consider alternatives** - are there other ways to achieve this?

## Documentation

### Types of Documentation

- **Code documentation**: Docstrings and inline comments
- **README.md**: Project overview and quick start
- **CONTRIBUTING.md**: This file
- **API documentation**: Generated from docstrings
- **Examples**: Sample code and use cases

### Updating Documentation

When making changes:

- Update relevant documentation files
- Keep examples up to date
- Add new sections for new features
- Fix typos and improve clarity

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

### Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- Project documentation (for major features)

## License

By contributing to paperless-docling-parser, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the "question" label
- Reach out to the maintainers
- Check existing issues and discussions

Thank you for contributing to paperless-docling-parser! 🎉