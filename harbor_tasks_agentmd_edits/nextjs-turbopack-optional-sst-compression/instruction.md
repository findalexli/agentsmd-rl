Refactor the `process_file` function in `main.py` to follow Python best practices.

The function currently:
- Uses `open()` without proper error handling
- Has a bare except clause
- Lacks type hints
- Lacks a docstring

Update the function to:
1. Use pathlib.Path instead of string paths
2. Add proper type hints
3. Add a docstring
4. Handle specific exceptions (FileNotFoundError, IOError)
5. Use a custom exception class for errors
