FROM php:8.3-cli

# Install required PHP extensions, Python, and tools
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libzip-dev \
    libonig-dev \
    python3 \
    python3-pip \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=995deea801b16b340d3331392e7b435c8648414c
RUN git clone --filter=blob:none --depth=100 --no-single-branch https://github.com/appwrite/appwrite.git appwrite && \
    cd appwrite && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/appwrite

# Install PHP dependencies (composer install)
# Use --no-dev for faster install and ignore platform requirements (ext-*)
RUN composer install --no-dev --optimize-autoloader --no-interaction \
    --ignore-platform-reqs 2>&1 || \
    (echo "Composer install with --ignore-platform-reqs failed, continuing anyway..." && true)

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
