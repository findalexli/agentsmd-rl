FROM php:8.3-cli

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    unzip \
    libzip-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions needed by Appwrite
RUN pip3 install --break-system-packages pytest

RUN docker-php-ext-install zip

# Set up working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout 96f4ef7d22ea9e12b5080268ed52a3b05b8649d9

# Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install PHP dependencies (only what's needed for syntax checking)
RUN cd /workspace/appwrite && \
    composer install --no-interaction --no-scripts --optimize-autoloader 2>&1 || true

# Create log directory
RUN mkdir -p /logs/verifier

# Set proper permissions
RUN chmod -R 755 /workspace/appwrite
