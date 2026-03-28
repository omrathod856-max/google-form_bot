# Use an official lightweight Python runtime
FROM python:3.10-slim

# Install Chromium, Chromium Driver, AND the C-compilers needed to build complex Python packages
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# CRITICAL FIX: Upgrade pip and build tools before installing packages to prevent metadata errors
RUN pip install --upgrade pip setuptools wheel

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port that Streamlit uses for the web dashboard
EXPOSE 8501

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
