# Dockerfile
FROM runpod/base:0.4.0-cuda11.8.0

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install runpod llama-cpp-python

# Create directory for handler
WORKDIR /app

# Copy files
COPY handler.py /app/handler.py
COPY requirements.txt /app/requirements.txt

# Install any additional requirements
RUN if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; fi

# Set the handler as entrypoint
CMD ["python", "-u", "/app/handler.py"]