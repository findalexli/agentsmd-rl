FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Set working directory
WORKDIR /workspace

# Clone appwrite repo at base commit
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite && \
    cd /workspace/appwrite && \
    git checkout d8f733787f0c24b99efa39f132af580c882c20d7

# Install PHP dependencies (optional - for syntax checking)
RUN cd /workspace/appwrite && \
    composer install --no-dev --no-interaction --optimize-autoloader 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/appwrite
