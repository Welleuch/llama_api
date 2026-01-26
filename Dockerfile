# Dockerfile - SIMPLER VERSION
FROM python:3.10-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install llama-cpp-python --no-cache-dir
RUN pip install runpod

# Copy ONLY handler.py
COPY handler.py /handler.py

# Run handler - IMPORTANT: Use absolute path
CMD ["python", "-u", "/handler.py"]