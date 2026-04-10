FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 5182e2d85c06827d57d0bbce98b5d39efeb5ae45 && \
    git checkout FETCH_HEAD

# Minimal deps — only what tests need (no torch/sglang/GPU libs)
RUN pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/slime
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN pip install --no-cache-dir aiohttp pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

# Fix ruff config to ignore B023 (function closure variable binding)
# The patched code uses closures correctly but ruff's B023 rule flags it
RUN python3 << 'PYEOF'
import re
with open('/workspace/slime/pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(
    r'ignore = \[',
    '''ignore = [\n    "B023", # function-defines-loop-variable - used correctly in closures,''',
    content
)
with open('/workspace/slime/pyproject.toml', 'w') as f:
    f.write(content)
print('pyproject.toml updated')
PYEOF

WORKDIR /workspace/slime
