FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Pin every test-time dep so reward is reproducible.
RUN pip install \
        sqlglot==28.10.1 \
        Jinja2==3.1.4 \
        Flask-Babel==4.0.0 \
        marshmallow==3.23.1 \
        pytest==8.3.4

# Clone Superset at the PR's base commit (the parent of the merge commit).
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
 && cd superset \
 && git checkout 18d89f25ce4db6258a01d409dd516003b1df7f0c

WORKDIR /workspace/superset

# Make the superset/ source tree importable without running its heavy
# top-level package init (which pulls in flask-appbuilder, SQLAlchemy, etc.).
# A conftest.py at /workspace/superset stubs sys.modules["superset"]
# before any test imports.
COPY conftest.py /workspace/superset/conftest.py

RUN mkdir -p /logs/verifier
