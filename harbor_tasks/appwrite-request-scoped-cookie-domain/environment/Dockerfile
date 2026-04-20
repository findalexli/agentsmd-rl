FROM php:8.3-cli

# Install git, python3, and dependencies for composer
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    curl \
    libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite && \
    cd /workspace/appwrite && \
    git checkout 2dce141d1747e95e50d8d9575baae1d8ac42699b

# Install PHP dependencies for syntax checking
RUN cd /workspace/appwrite && \
    composer install --no-interaction --optimize-autoloader 2>/dev/null || true
