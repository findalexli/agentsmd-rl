FROM swift:5.9-slim

# Install git and python3 for testing
RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# Clone the Kotlin repository and checkout base commit (parent of merge)
ENV REPO_DIR=/workspace/kotlin
ENV MERGE_COMMIT=7766376a2d2a7276b678d81c2d592d89362f1d3b

RUN mkdir -p /workspace && \
    git clone --filter=blob:none https://github.com/JetBrains/kotlin.git $REPO_DIR && \
    cd $REPO_DIR && \
    git fetch --depth=200 origin $MERGE_COMMIT && \
    git checkout $MERGE_COMMIT && \
    git checkout HEAD^1

# Install pytest in a virtual environment
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest
ENV PATH="/opt/venv/bin:$PATH"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR $REPO_DIR
