# ---- Base Stage ----
    FROM python:3.11 as base
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_DEFAULT_TIMEOUT=100 \
        DISPLAY=host.docker.internal:0
    
    WORKDIR /app
    
    # ---- Builder Stage ----
    FROM base as builder
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        tk-dev \
        python3-tk \
        && rm -rf /var/lib/apt/lists/*
    
    # Install requirements globally (not as user)
    COPY requirements.txt .
    RUN grep -v "^logging==" requirements.txt > filtered_requirements.txt && \
    pip install --no-cache-dir -r filtered_requirements.txt
    
    # Copy application code
    COPY . .
    
    # ---- Production Stage ----
    FROM base as production
    WORKDIR /app
    
    # Runtime dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libjpeg62-turbo \
        zlib1g \
        python3-tk \
        xauth \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy from builder
    COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
    COPY --from=builder /usr/local/bin /usr/local/bin
    COPY . .
    
    # Set the working directory to the app location    
    CMD ["python", "entry_inventory.py"]