FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    UV_LINK_MODE=copy \
    LOG_PATH=/tmp/odin.log

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

ARG UV_VERSION=0.12.17
ARG TARGETARCH
ARG TARGETVARIANT

# ghcr.io/astral-sh/uv has no linux/arm/v7 image, fetch the standalone binary instead
RUN set -e; \
    case "${TARGETARCH}/${TARGETVARIANT}" in \
        amd64/) UV_TRIPLE=x86_64-unknown-linux-gnu ;; \
        arm64/) UV_TRIPLE=aarch64-unknown-linux-gnu ;; \
        arm/v7) UV_TRIPLE=armv7-unknown-linux-gnueabihf ;; \
        *) echo "unsupported architecture: ${TARGETARCH}/${TARGETVARIANT}" >&2; exit 1 ;; \
    esac; \
    curl -LsSf "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_TRIPLE}.tar.gz" \
        -o /tmp/uv.tar.gz; \
    tar -xzf /tmp/uv.tar.gz -C /tmp; \
    mv "/tmp/uv-${UV_TRIPLE}/uv" "/tmp/uv-${UV_TRIPLE}/uvx" /bin/; \
    rm -rf /tmp/uv.tar.gz "/tmp/uv-${UV_TRIPLE}"

RUN uv python install 3.13 \
    && ln -sf "$(uv python find 3.13)" /usr/local/bin/python3 \
    && ln -sf "$(uv python find 3.13)" /usr/local/bin/python \
    && git config --global --add safe.directory /app

WORKDIR /app
