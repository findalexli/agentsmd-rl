FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Setup prettier with Svelte plugin in /opt/prettier
RUN mkdir -p /opt/prettier && cd /opt/prettier && \
    npm init -y && \
    npm install prettier prettier-plugin-svelte

# Add prettier to PATH and set plugin search dir
ENV PATH="/opt/prettier/node_modules/.bin:${PATH}"
ENV PRETTIER_PLUGIN_SEARCH_DIR="/opt/prettier/node_modules"

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin bb127c74bd6301e3782e0ce4744161ae976a8481 && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (no frontend build needed)
RUN cd /workspace/gradio && pip install --no-cache-dir -e ".[dev]" 2>&1 | tail -5

ENV PYTHONPATH=/workspace/gradio
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir numpy Pillow

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio
