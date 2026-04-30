FROM python:3.10-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System libs needed by superset's core deps (cryptography, lxml, pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        libssl-dev \
        libffi-dev \
        libsasl2-dev \
        libldap2-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        zlib1g-dev \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 5263abdc60ef790c649d799f4485c1f9f028e86b

WORKDIR /workspace/superset

# Pin pip/setuptools to known-good versions for reproducibility.
RUN pip install --upgrade pip==24.3.1 setuptools==75.6.0 wheel==0.45.1

# Install superset (no DB/cloud extras) plus the minimal test dependencies.
# The full development extras pull in many tools we don't need (pre-commit,
# pylint, ruff, etc.); we only need pytest + pytest-mock for the unit tests.
RUN pip install -e . \
    && pip install \
        pytest==7.4.4 \
        pytest-mock==3.14.0 \
        pytest-json-ctrf==0.3.5 \
        parameterized==0.9.0 \
        freezegun==1.5.1

# Sanity check: the file the agent must edit exists at the expected path.
RUN test -f /workspace/superset/superset/daos/report.py \
    && grep -q 'find_by_extra_metadata' /workspace/superset/superset/daos/report.py

RUN mkdir -p /logs/verifier
