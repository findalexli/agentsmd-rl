FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential pkg-config \
        libssl-dev libpq-dev libffi-dev libsasl2-dev libldap2-dev \
        default-libmysqlclient-dev libxmlsec1-dev libxml2-dev libxslt1-dev \
        libcairo2-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout fc156d0014b032bbd10548e8167426d5b32e5f8e

WORKDIR /workspace/superset

RUN pip install --upgrade pip==25.0.1 setuptools==75.8.0 wheel==0.45.1

# Install pinned dev requirements (these include base.txt at FAB 5.0.2 baseline)
RUN pip install -r requirements/development.txt

# Install superset itself in editable mode (no extra deps beyond what's pinned)
RUN pip install -e . --no-deps

# Pre-install pytest and friends so test.sh doesn't need network
RUN pip install pytest==8.3.4 pytest-mock==3.14.0 pytest-json-ctrf==0.3.7

# Ensure FAB is at 5.1.0 so AUTH_SAML constant exists in the test environment.
# The PR's gold solution upgrades FAB; we install 5.1.0 in the image so the
# test infrastructure can reference AUTH_SAML even on the base commit (where
# the agent's job is to add the SAML branch in views/base.py and config.py).
RUN pip install "flask-appbuilder==5.1.0"

RUN mkdir -p /logs/verifier
