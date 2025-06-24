FROM ghcr.io/open-webui/pipelines:main

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt --no-cache-dir

COPY agents   ./agents
COPY libs     ./libs
COPY tools     ./tools
COPY pipelines ./pipelines
