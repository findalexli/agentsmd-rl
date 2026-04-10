# Use the official ClickHouse binary builder image which has all dependencies
FROM clickhouse/binary-builder:latest

# Install pytest via pip (lightweight)
RUN pip3 install pytest

# Create necessary directories - repo will be mounted
RUN mkdir -p /workspace/ClickHouse /logs/verifier

WORKDIR /workspace/ClickHouse

# Default command keeps container running for test execution
CMD ["/bin/bash"]
