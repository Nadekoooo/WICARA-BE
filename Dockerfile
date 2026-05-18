FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        ffmpeg \
        fonts-dejavu-core \
        fonts-noto-core \
        libcairo2-dev \
        libpango1.0-dev \
        libsox-fmt-all \
        nodejs \
        npm \
        pkg-config \
        sox \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -e ".[render]" \
    && if [ -f wicara_remotion_templates/package-lock.json ]; then \
        npm ci --prefix wicara_remotion_templates; \
    fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
