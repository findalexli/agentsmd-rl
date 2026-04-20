FROM php:8.3-cli

# Install git, python3, and dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    libzip-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions needed by Appwrite
RUN docker-php-ext-install zip

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Set working directory
WORKDIR /workspace

# Clone Appwrite repo at base commit
ARG REPO=appwrite/appwrite
ARG BASE_COMMIT=1ab05acc93a9f3c9b1e4dfb55dded2597f06a838

RUN git clone --filter=blob:none https://github.com/${REPO}.git appwrite && \
    cd appwrite && \
    git checkout ${BASE_COMMIT}

# Install PHP dependencies (composer install without scripts to avoid issues)
WORKDIR /workspace/appwrite
RUN composer install --no-interaction --no-scripts --optimize-autoloader 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/appwrite
