FROM eclipse-temurin:21-jdk

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest pyyaml --quiet

# Download jspecify annotation jar for compilation
RUN mkdir -p /opt/jspecify && \
    curl -L -o /opt/jspecify/jspecify-1.0.0.jar \
    https://repo1.maven.org/maven2/org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar

# Test file will be mounted at runtime from /tmp/tests

# Create the fixed test runner script inline
RUN cat > /usr/local/bin/test-runner.sh << 'TESTEOF'
#!/bin/bash

echo "Installing pytest..."
pip3 install --break-system-packages pytest pyyaml --quiet 2>/dev/null || pip3 install pytest pyyaml --quiet

echo "Running tests..."
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 = fail, 1 = pass)
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward
    echo "SUCCESS: All tests passed"
else
    echo 0 > /logs/verifier/reward
    echo "FAILURE: Some tests failed"
fi

exit $exit_code
TESTEOF
RUN chmod +x /usr/local/bin/test-runner.sh

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium

WORKDIR /workspace/selenium
RUN git checkout 4bb23f484eec6f986b563fb3146cb64dcbcc0187

RUN mkdir -p /logs/verifier
