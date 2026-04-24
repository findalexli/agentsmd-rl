FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin e931ab4802816cec55aa5a25b51f27cb941c924e && \
    git checkout FETCH_HEAD

# Install minimal deps needed for fx graph pickling tests
RUN pip install --no-cache-dir numpy sympy dill typing_extensions 2>/dev/null || true

# Create the missing torch/version.py stub required by torch.torch_version
RUN python3 << 'PYEOF'
import os
ver_dir = '/workspace/pytorch/torch'
ver_file = os.path.join(ver_dir, 'version.py')
if not os.path.exists(ver_file):
    with open(ver_file, 'w') as f:
        f.write('__version__ = "2.5.0+dev"\ninternal_version = __version__\n')
    print('Created version.py stub')
PYEOF

# Disable loading of libtorch_global_deps.so which is not present in sparse checkout
RUN sed -i 's/USE_GLOBAL_DEPS = True/USE_GLOBAL_DEPS = False/' /workspace/pytorch/torch/_utils_internal.py

ENV PYTHONPATH="/workspace/pytorch"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/pytorch