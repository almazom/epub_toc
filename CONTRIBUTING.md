# Contributing to EPUB TOC

Thank you for your interest in our project! We welcome any help with:
- Bug reports
- Documentation improvements
- Bug fixes
- New features

## Development Process

1. Create an issue to discuss proposed changes
2. Fork the repository and create a branch for your changes
3. Write tests for new functionality
4. Ensure code meets standards:
   - Use black for formatting
   - Follow PEP 8
   - Add type hints
   - Write docstrings in Google format
5. Make sure all tests pass
6. Create a Pull Request

## Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/epub_toc.git
cd epub_toc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
pytest
```

## Code Style

We use:
- black for code formatting
- isort for import sorting
- pylint for code checking
- mypy for type checking

## Commits

- Use clear commit messages
- One commit = one logical change
- Start message with imperative verb

Examples:
```
Add support for EPUB 3.0
Fix parsing of nested lists
Update documentation for new features
```

## Pull Requests

- Create PR from a separate branch
- Describe changes in detail
- Reference related issues
- Add screenshots for UI changes
- Update documentation

## Questions

If you have questions:
1. Check existing issues
2. Create new issue with "question" label
3. Join discussions in Discussions 