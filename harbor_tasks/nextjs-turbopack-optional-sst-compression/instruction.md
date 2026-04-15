Refactor the `process_file` function in `main.py` to follow Python best practices.

## Expected behavior

The `process_file` function must read a text file and return its content as an uppercase string. For example, if a file contains `hello world`, calling `process_file` on that file should return `HELLO WORLD`.

When a file cannot be found or read, the function should raise a custom `FileProcessingError` exception that preserves the original error message.

## Current issues

The existing implementation uses `open()` without proper error handling, has a bare `except:` clause, lacks type hints, and lacks a docstring.

## Required changes

1. **Use `pathlib.Path`**: Accept `pathlib.Path` objects and use the `read_text()` method for reading file contents instead of the built-in `open()` function.
2. **Add type hints**: Annotate the `filepath` parameter as `Path` and the return type as `str`.
3. **Add a docstring**: Include `Args:` and `Returns:` sections in the docstring describing the parameter and return value.
4. **Handle specific exceptions**: Replace the bare `except:` clause with explicit handling of `FileNotFoundError` and `IOError`.
5. **Define a custom exception**: Create a class named `FileProcessingError` (subclassing `Exception`) that is raised when file processing fails, preserving the error message.
