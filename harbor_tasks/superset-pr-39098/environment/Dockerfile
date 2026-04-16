FROM python:3.12-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone repository with filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset

# Checkout base commit (parent of merge commit)
WORKDIR /workspace/superset
RUN git checkout 7c79b9ab6184cf42571f316e81e52767e044fa8d

# Install minimal dependencies needed for testing the security manager
# We don't need the full superset install - just enough to import the module
RUN pip install --no-cache-dir \
    flask \
    flask-appbuilder \
    flask-login \
    flask-wtf \
    sqlalchemy \
    werkzeug \
    pyyaml \
    marshmallow \
    deprecation \
    pandas \
    numpy \
    cachelib \
    celery \
    redis \
    selenium \
    slack_sdk \
    tabulate \
    wtforms \
    python-dateutil \
    packaging \
    croniter \
    isodate \
    mypy

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
