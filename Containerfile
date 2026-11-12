# Cairn: Fedora Kinoite (Fedora Atomic + KDE Plasma) plus Cairn's apps, look and settings.
# The whole operating system is built from this file, like a Docker image.
# Build locally with:  podman build -t cairn .

ARG FEDORA_VERSION=43
ARG BASE_IMAGE=quay.io/fedora-ostree-desktops/kinoite

# Stage 1: the parts of this repository the build needs, mounted at /ctx in stage 2.
FROM scratch AS ctx
COPY build_files /build_files
COPY brand /brand
COPY system_files /system_files

# Stage 2: start from Fedora's official Kinoite image and change it.
FROM ${BASE_IMAGE}:${FEDORA_VERSION}

ARG CAIRN_VERSION

RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    CAIRN_VERSION="${CAIRN_VERSION}" /ctx/build_files/build.sh && \
    ostree container commit

# Checks the result is a valid bootable image.
RUN bootc container lint
