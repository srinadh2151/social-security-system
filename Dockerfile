# UAE Social Security System - Multi-stage Docker Build
# This Dockerfile creates an optimized production image

# ===================================
# Stage 1: Base Python Environment
# ===================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-ara \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# ===================================
# Stage 2: Dependencies Installation
# ===================================
FROM base as dependencies

# Copy requirements files
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ===================================
# Stage 3: Application Build
# ===================================
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/backend/uploads \
    /app/workflow_outputs \
    /app/temp_docs \
    /app/logs

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# ===================================
# Stage 4: Production Image
# ===================================
FROM application as production

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "backend/main.py"]

# ===================================
# Labels for metadata
# ===================================
LABEL maintainer="UAE Social Security Team" \
      version="1.0.0" \
      description="UAE Social Security Application System"