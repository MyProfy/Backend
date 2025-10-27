FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (added curl ✅)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY backend/ .

# Expose port (optional)
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]