# Documentation Standards

## Python Docstrings

### Module Level
```python
"""
Module description.

This module provides functionality for...

Examples:
    Basic usage:
    >>> from module import Class
    >>> obj = Class()
    >>> obj.method()

Notes:
    Any important notes about the module.
"""
```

### Class Level
```python
"""
Class description.

This class implements...

Attributes:
    attr_name (type): Description of the attribute.

Examples:
    Basic instantiation:
    >>> obj = ClassName(param='value')
    >>> result = obj.method()

Notes:
    Any important implementation notes.
"""
```

### Method Level
```python
"""
Method description.

Detailed explanation of what the method does.

Args:
    param1 (type): Description of first parameter.
    param2 (type, optional): Description of optional parameter.
        Defaults to None.

Returns:
    type: Description of return value.

Raises:
    ExceptionType: When and why this exception is raised.

Examples:
    >>> obj.method('param')
    'result'

Notes:
    Any implementation notes or caveats.
"""
```

## Documentation Rules

1. All public modules, classes, methods, and functions MUST have docstrings
2. Use Google-style docstring format
3. Include type hints in both docstring and function signature
4. Provide at least one usage example for each public interface
5. Document all exceptions that may be raised
6. Keep examples simple and focused
7. Update documentation when changing code

## File Structure
- `/docs/` - Documentation root
  - `api/` - API documentation
  - `examples/` - Code examples
  - `guides/` - User and developer guides
  - `DOCUMENTATION_STANDARD.md` - This file
  - `CHANGELOG.md` - Version history 