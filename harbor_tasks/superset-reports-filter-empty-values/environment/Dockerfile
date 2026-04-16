FROM python:3.12-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone Superset repo at base commit (shallow clone for speed)
# Base commit: 6ba90968701fbce377d6479842329fed86c31e4f
RUN git clone --depth 100 --filter=blob:none https://github.com/apache/superset.git \
    && cd superset \
    && git fetch --depth=1 origin 6ba90968701fbce377d6479842329fed86c31e4f \
    && git checkout 6ba90968701fbce377d6479842329fed86c31e4f

WORKDIR /workspace/superset

# Install Python dependencies from requirements
RUN pip install --no-cache-dir \
    pytest \
    pytest-mock \
    prison \
    cron-descriptor \
    Flask \
    Flask-AppBuilder \
    SQLAlchemy \
    sqlalchemy-utils \
    alembic \
    pandas \
    marshmallow

# Create a minimal conftest.py to avoid the full test setup
RUN mkdir -p /workspace/superset/tests/unit_tests/reports && \
    echo '# Minimal conftest for unit tests\nimport sys\nimport os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))\n' > /workspace/superset/tests/unit_tests/reports/conftest.py

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
