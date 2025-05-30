# ---- Base Stage ----
    FROM python:3.11-slim as base

    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_DEFAULT_TIMEOUT=100 \
        DISPLAY=host.docker.internal:0 \
        API_BASE_URL=${API_BASE_URL:-"http://localhost:8000/api/v1/"} \
        PATH="/opt/venv/bin:$PATH"
    
    WORKDIR /app
    
    # Create non-root user early for better layer caching
    ARG USER_ID=1000
    ARG GROUP_ID=1000
    RUN groupadd -g ${GROUP_ID} appuser && \
        useradd -u ${USER_ID} -g appuser -s /bin/sh -m appuser && \
        mkdir -p /app/app/credentials/users && \
        chown -R appuser:appuser /app
    
    # ---- Builder Stage ----
    FROM base as builder
    
    # Install build dependencies (keeping them separate for better caching)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        libzbar-dev \
        && rm -rf /var/lib/apt/lists/*
    
    # Create virtual environment
    RUN python -m venv /opt/venv
    
    # Install Python dependencies
    COPY --chown=appuser:appuser requirements.txt .
    RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
        /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
    
    # Copy only what's needed for building
    COPY --chown=appuser:appuser app/ ./app/
    
    # ---- Production Stage ----
    FROM base as production
    
    # Install only runtime dependencies (minimal set)
    RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    xauth \
    libzbar0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Copy virtual environment from builder
    COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
    
    # Copy application code (from base to avoid rebuilding everything)
    COPY --chown=appuser:appuser . .
    
    # Ensure proper permissions
    RUN chown -R appuser:appuser /app
    
    # Switch to non-root user
    USER appuser
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
        CMD curl -f http://localhost:8000/health || exit 1
    
    # Expose the port the app runs on
    EXPOSE 8000
    
    # Command to run the application
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]