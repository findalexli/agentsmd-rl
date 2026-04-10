FROM php:8.3-cli

# Install git, python3, pip, and php extensions
RUN apt-get update && apt-get install -y     git     python3     python3-pip     python3-venv     libonig-dev     libzip-dev     unzip     && rm -rf /var/lib/apt/lists/*

# Install PHP zip extension for composer
RUN docker-php-ext-install zip

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Create working directory
WORKDIR /workspace

# Clone appwrite repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --single-branch     https://github.com/appwrite/appwrite.git appwrite &&     cd appwrite &&     git checkout 1aa2c7ff2b5216803cb50c0faea58ce2ae380b3f

# Set working directory to the repo
WORKDIR /workspace/appwrite

# Install PHP dependencies (ignoring platform requirements for test environment)
RUN composer install --ignore-platform-reqs --no-interaction --optimize-autoloader

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Create symlink for tests directory so test.sh paths work
RUN ln -s /tests /workspace/tests

# Install pytest
RUN pip3 install pytest --break-system-packages
