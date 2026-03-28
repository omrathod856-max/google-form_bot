# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install Chromium, Driver, AND the C-compilers needed for Numpy
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Upgrade pip and build tools FIRST
RUN pip install --upgrade pip setuptools wheel

# Now install your requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the bot when the container launches
CMD ["python", "app.py"]
