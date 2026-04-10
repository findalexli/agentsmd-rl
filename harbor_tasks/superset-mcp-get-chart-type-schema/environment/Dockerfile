# Apache Superset MCP Service - get_chart_type_schema tool task
FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=8e811de5643022a97f6cb1890aa513197b7312e4
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/superset.git superset && \
    cd superset && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies (minimal for MCP service testing)
WORKDIR /workspace/superset
RUN pip install --no-cache-dir \
    pydantic>=2.0.0 \
    pytest \
    pytest-mock \
    "fastmcp>=2.0.0" \
    -e .

# Create log directory
RUN mkdir -p /logs/verifier

# Fix: Replace the placeholder tool decorator with a working implementation
RUN python3 << 'EOF'
import sys
import os

decorators_path = None
for p in sys.path:
    if 'site-packages' in p:
        try:
            candidate = os.path.join(p, 'superset_core/mcp/decorators.py')
            if os.path.exists(candidate):
                decorators_path = candidate
                break
        except:
            pass

if decorators_path:
    # Write a complete replacement file with working implementations
    new_content = '''# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
MCP (Model Context Protocol) tool registration for Superset MCP server.
"""

from typing import Any, Callable, TypeVar
from functools import wraps

F = TypeVar("F", bound=Callable[..., Any])


class ToolAnnotations:
    """Annotations for MCP tools."""
    def __init__(self, title=None, readOnlyHint=None, destructiveHint=None, openWorldHint=None):
        self.title = title
        self.readOnlyHint = readOnlyHint
        self.destructiveHint = destructiveHint
        self.openWorldHint = openWorldHint


def tool(
    func_or_name: str | Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    protect: bool = True,
    class_permission_name: str | None = None,
    annotations: Any = None,
    **kwargs,
) -> Any:
    """Working decorator for MCP tools - stores metadata on the function."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store tool metadata on the wrapper function
        wrapper._mcp_tool = True
        wrapper._tool_name = name or func.__name__
        wrapper._tool_description = description or (func.__doc__ or "")
        wrapper._tool_tags = tags or []
        wrapper._tool_protect = protect
        wrapper._tool_class_permission_name = class_permission_name
        wrapper._tool_annotations = annotations

        return wrapper

    # Handle both @tool and @tool(...) syntax
    if callable(func_or_name):
        # Used as @tool (without parentheses)
        func = func_or_name
        return decorator(func)
    else:
        # Used as @tool(...) (with parentheses, possibly with name)
        return decorator


def prompt(
    func_or_name: str | Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    title: str | None = None,
    description: str | None = None,
    tags: set[str] | None = None,
    protect: bool = True,
) -> Any:
    """Working decorator for MCP prompts."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._mcp_prompt = True
        return wrapper

    if callable(func_or_name):
        return decorator(func_or_name)
    else:
        return decorator


__all__ = [
    "tool",
    "prompt",
    "ToolAnnotations",
]
'''
    with open(decorators_path, 'w') as f:
        f.write(new_content)
    print(f'Replaced decorators.py with working implementation at {decorators_path}')
else:
    print('Could not find decorators.py')
EOF

# Set working directory for tests
WORKDIR /workspace
