FROM docker.io/library/fedora:28

ENV PYCURL_SSL_LIBRARY=openssl

RUN \
    dnf install -y \
        gcc \
        libcurl-devel \
        libxml2-devel \
        openssh-clients \
        openssl-devel \
        python3 \
        python3-pip \
        python3-devel \
        which

RUN \
    ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip \
    && pip install --upgrade pip \
    && pip install pipenv \
    && dnf clean all \
    && mkdir -p /app

WORKDIR /app

CMD ["echo", "This is a base image and isn't meant to be run directly."]
