FROM python:3.11-slim AS builder

# Build wheels in an isolated stage so the runtime image stays lean.
WORKDIR /app

# Install build tools needed if any dependency, such as pyswisseph, needs compilation.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first for better Docker layer caching.
COPY requirements.txt .

# Build dependency wheels without keeping pip cache.
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM python:3.11-slim

# Keep Python container behavior production-friendly and point Swiss Ephemeris to bundled data.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SWISSEPH_EPHE_PATH=/app/ephe

# Set the application working directory.
WORKDIR /app

# Install dependencies from prebuilt wheels without pip cache.
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy the FastAPI app, scripts, and examples (ephe/ is gitignored; fetched below).
COPY . .

# Download Swiss Ephemeris data files at build time so the image is self-contained.
# These are not in the repo (gitignored) but are required at runtime.
RUN mkdir -p /app/ephe \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q -O /app/ephe/sepl_18.se1 \
       https://github.com/aloistr/swisseph/raw/master/ephe/sepl_18.se1 \
    && wget -q -O /app/ephe/semo_18.se1 \
       https://github.com/aloistr/swisseph/raw/master/ephe/semo_18.se1

# Run as a non-root user for safer production execution.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose Google Cloud Run's standard HTTP port.
EXPOSE 8080

# Start Uvicorn on all interfaces for Cloud Run.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
