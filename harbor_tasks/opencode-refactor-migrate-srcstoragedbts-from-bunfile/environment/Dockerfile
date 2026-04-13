FROM python:3.11-slim

WORKDIR /workspace/calculator

# Copy the calculator module
COPY calculator.py .

# Install pytest for running tests
RUN pip install pytest

CMD ["python3", "-c", "print('Calculator module ready')"]
