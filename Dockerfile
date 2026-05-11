# Job Market Intelligence Pipeline - Production Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for database connectivity
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY frontend/ ./frontend/

# Create data storage directories
RUN mkdir -p data/raw data/processed

# Expose application ports
EXPOSE 8000 8501

# Start API server by default
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
