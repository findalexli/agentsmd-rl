FROM php:8.3-cli-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libzip-dev \
    libssl-dev \
    pkg-config \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install zip

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /workspace

# Clone appwrite repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite && \
    cd /workspace/appwrite && \
    git checkout 6e1f0d57af305affe7dbebf9d71f19ec4d6f68e5

# Install PHP dependencies
WORKDIR /workspace/appwrite
RUN composer install --no-interaction --optimize-autoloader --no-scripts 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set back to workspace
WORKDIR /workspace
