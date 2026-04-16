#!/bin/bash
set -e

cd /workspace/pulumi

# Fix _types.py - add @functools.cache to _py_properties and _types_from_py_properties
python3 << 'EOF'
import re

# Read the file
with open('sdk/python/lib/pulumi/_types.py', 'r') as f:
    content = f.read()

# Fix 1: Modify _py_properties function - add @functools.cache and change to return tuple
old_py_properties = '''def _py_properties(cls: type) -> Iterator[tuple[str, str, builtins.property]]:
    for base in reversed(cls.__mro__):
        for python_name, v in base.__dict__.items():
            if isinstance(v, builtins.property):
                prop = cast(builtins.property, v)
                pulumi_name = getattr(prop.fget, _PULUMI_NAME, MISSING)
                if pulumi_name is not MISSING:
                    yield (python_name, cast(str, pulumi_name), prop)'''

new_py_properties = '''@functools.cache
def _py_properties(cls: type) -> tuple[tuple[str, str, builtins.property], ...]:
    result: list[tuple[str, str, builtins.property]] = []
    for base in reversed(cls.__mro__):
        for python_name, v in base.__dict__.items():
            if isinstance(v, builtins.property):
                prop = cast(builtins.property, v)
                pulumi_name = getattr(prop.fget, _PULUMI_NAME, MISSING)
                if pulumi_name is not MISSING:
                    result.append((python_name, cast(str, pulumi_name), prop))
    return tuple(result)'''

content = content.replace(old_py_properties, new_py_properties)

# Fix 2: Add type: ignore[arg-type] comments to _py_properties calls
content = content.replace(
    'for python_name, _, prop in _py_properties(cls):',
    'for python_name, _, prop in _py_properties(cls):  # type: ignore[arg-type] # https://github.com/python/mypy/issues/11470'
)

content = content.replace(
    'for _, pulumi_name, prop in _py_properties(cls):',
    'for _, pulumi_name, prop in _py_properties(cls):  # type: ignore[arg-type] # https://github.com/python/mypy/issues/11470'
)

# Handle the third case for output_type
content = content.replace(
    'for python_name, pulumi_name, _ in _py_properties(cls):',
    'for python_name, pulumi_name, _ in _py_properties(cls):  # type: ignore[arg-type] # https://github.com/python/mypy/issues/11470',
    2  # Only replace first 2 occurrences
)

# Fix 3: Add @functools.cache to _types_from_py_properties
old_types_from = '''def _types_from_py_properties(cls: type) -> dict[str, type]:
    """
    Returns a dict of Pulumi names to types for a type.'''

new_types_from = '''@functools.cache
def _types_from_py_properties(cls: type) -> dict[str, type]:
    """
    Returns a dict of Pulumi names to types for a type.'''

content = content.replace(old_types_from, new_types_from)

# Write the file
with open('sdk/python/lib/pulumi/_types.py', 'w') as f:
    f.write(content)

print("Fixed _types.py")
EOF

# Fix known_types.py - add module-level caching
python3 << 'EOF'
# Read the file
with open('sdk/python/lib/pulumi/runtime/known_types.py', 'r') as f:
    content = f.read()

# Add module-level cache variables after the imports
old_import = '''from typing import Any


def is_asset'''

new_import = '''from typing import Any

# Cache class references to avoid repeated import machinery overhead. These functions are called *a lot* during
# serialization, so this optimization does add up.
_Asset: type | None = None
_Archive: type | None = None
_Resource: type | None = None
_CustomResource: type | None = None
_CustomTimeouts: type | None = None
_Stack: type | None = None
_Output: type | None = None
_Unknown: type | None = None


def is_asset'''

content = content.replace(old_import, new_import)

# Fix is_asset
content = content.replace(
    '''def is_asset(obj: Any) -> bool:
    """
    Returns true if the given type is an Asset, false otherwise.
    """
    from .. import Asset

    return isinstance(obj, Asset)''',
    '''def is_asset(obj: Any) -> bool:
    """
    Returns true if the given type is an Asset, false otherwise.
    """
    global _Asset  # noqa: PLW0603
    if _Asset is None:
        from .. import Asset

        _Asset = Asset
    return isinstance(obj, _Asset)'''
)

# Fix is_archive
content = content.replace(
    '''def is_archive(obj: Any) -> bool:
    """
    Returns true if the given type is an Archive, false otherwise.
    """
    from .. import Archive

    return isinstance(obj, Archive)''',
    '''def is_archive(obj: Any) -> bool:
    """
    Returns true if the given type is an Archive, false otherwise.
    """
    global _Archive  # noqa: PLW0603
    if _Archive is None:
        from .. import Archive

        _Archive = Archive
    return isinstance(obj, _Archive)'''
)

# Fix is_resource
content = content.replace(
    '''def is_resource(obj: Any) -> bool:
    """
    Returns true if the given type is a Resource, false otherwise.
    """
    from .. import Resource

    return isinstance(obj, Resource)''',
    '''def is_resource(obj: Any) -> bool:
    """
    Returns true if the given type is a Resource, false otherwise.
    """
    global _Resource  # noqa: PLW0603
    if _Resource is None:
        from .. import Resource

        _Resource = Resource
    return isinstance(obj, _Resource)'''
)

# Fix is_custom_resource
content = content.replace(
    '''def is_custom_resource(obj: Any) -> bool:
    """
    Returns true if the given type is a CustomResource, false otherwise.
    """
    from .. import CustomResource

    return isinstance(obj, CustomResource)''',
    '''def is_custom_resource(obj: Any) -> bool:
    """
    Returns true if the given type is a CustomResource, false otherwise.
    """
    global _CustomResource  # noqa: PLW0603
    if _CustomResource is None:
        from .. import CustomResource

        _CustomResource = CustomResource
    return isinstance(obj, _CustomResource)'''
)

# Fix is_custom_timeouts
content = content.replace(
    '''def is_custom_timeouts(obj: Any) -> bool:
    """
    Returns true if the given type is a CustomTimeouts, false otherwise.
    """
    from .. import CustomTimeouts

    return isinstance(obj, CustomTimeouts)''',
    '''def is_custom_timeouts(obj: Any) -> bool:
    """
    Returns true if the given type is a CustomTimeouts, false otherwise.
    """
    global _CustomTimeouts  # noqa: PLW0603
    if _CustomTimeouts is None:
        from .. import CustomTimeouts

        _CustomTimeouts = CustomTimeouts
    return isinstance(obj, _CustomTimeouts)'''
)

# Fix is_stack
content = content.replace(
    '''def is_stack(obj: Any) -> bool:
    """
    Returns true if the given type is a Stack, false otherwise.
    """
    from .stack import Stack

    return isinstance(obj, Stack)''',
    '''def is_stack(obj: Any) -> bool:
    """
    Returns true if the given type is a Stack, false otherwise.
    """
    global _Stack  # noqa: PLW0603
    if _Stack is None:
        from .stack import Stack

        _Stack = Stack
    return isinstance(obj, _Stack)'''
)

# Fix is_output
content = content.replace(
    '''def is_output(obj: Any) -> bool:
    """
    Returns true if the given type is an Output, false otherwise.
    """
    from .. import Output

    return isinstance(obj, Output)''',
    '''def is_output(obj: Any) -> bool:
    """
    Returns true if the given type is an Output, false otherwise.
    """
    global _Output  # noqa: PLW0603
    if _Output is None:
        from .. import Output

        _Output = Output
    return isinstance(obj, _Output)'''
)

# Write the file
with open('sdk/python/lib/pulumi/runtime/known_types.py', 'w') as f:
    f.write(content)

print("Fixed known_types.py")
EOF

echo "Patch applied successfully"
