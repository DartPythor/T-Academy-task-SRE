#!/bin/bash
set -euo pipefail

VERSION="${VERSION:-0.1.0}"
GIT_SHA="${GIT_SHA:-$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")}"
BUILD_DATE="${BUILD_DATE:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"

IMAGE_NAME="vacancy-analyzer"

echo "Building ${IMAGE_NAME}:${VERSION} (sha: ${GIT_SHA}, date: ${BUILD_DATE})"

docker build \
    --build-arg VERSION="${VERSION}" \
    --build-arg GIT_SHA="${GIT_SHA}" \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    -t "${IMAGE_NAME}:${VERSION}-${GIT_SHA}" \
    -t "${IMAGE_NAME}:latest" \
    .

echo "Done: ${IMAGE_NAME}:${VERSION}-${GIT_SHA}"
docker inspect "${IMAGE_NAME}:${VERSION}-${GIT_SHA}" --format='{{index .Config.Labels "org.opencontainers.image.version"}}' 2>/dev/null && echo "Labels verified" || echo "Warning: labels not set"
