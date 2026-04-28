FROM php:8.3-cli

# Install Python3, pip, git, and composer dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Composer (pinned to v2.7.7 via GitHub release)
RUN curl -L -o /usr/bin/composer https://github.com/composer/composer/releases/download/2.7.7/composer.phar && \
    chmod +x /usr/bin/composer

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone appwrite repo at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout 20f80ac067e0042ea05ac9566f0a9ff1624bf3b2

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
