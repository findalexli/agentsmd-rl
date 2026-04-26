FROM php:8.3-cli

# Install Python3, pip, git, and composer dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone appwrite repo at base commit (before fix)
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/appwrite/appwrite.git && \
    git fetch --depth=1 origin 20f80ac067e0042ea05ac9566f0a9ff1624bf3b2 && \
    git checkout FETCH_HEAD

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
