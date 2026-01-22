# Sovereign LNT Dockerfile
# Optimized for Canadian Hydro-Powered Data Centers
FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SOVEREIGN_MODE 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure log directories exist
RUN mkdir -p flywheel_logs

# Default command: Launch the Sovereign CLI
CMD ["python", "lnt_cli.py"]
