FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Clone sglang at the commit BEFORE the fix
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 2acdda1d850122129c6ff21b6d07b2a4c9eb31bd && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (CPU-only torch, pybase64, Pillow)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir pybase64 Pillow psutil numpy tqdm

# Install linting tools for repo_tests (matching .pre-commit-config.yaml versions)
RUN pip install --no-cache-dir ruff==0.15.1 black==26.1.0 isort==7.0.0 codespell==2.4.1

ENV PYTHONPATH="/workspace/sglang/python"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/sglang
