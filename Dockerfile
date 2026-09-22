FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    UV_LINK_MODE=copy \
    LOG_PATH=/tmp/odin.log

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv python install 3.13 \
    && ln -sf "$(uv python find 3.13)" /usr/local/bin/python3 \
    && ln -sf "$(uv python find 3.13)" /usr/local/bin/python \
    && git config --global --add safe.directory /app

WORKDIR /app
