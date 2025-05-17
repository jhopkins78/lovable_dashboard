# syntax=docker/dockerfile:1

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed, e.g. gcc for some pip installs)
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get purge -y --auto-remove build-essential

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables (optional, for unbuffered logs)
ENV PYTHONUNBUFFERED=1

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
