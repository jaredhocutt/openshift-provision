FROM docker.io/library/fedora:28

RUN \
    dnf install -y \
        openssh-clients \
        python3 \
        python3-pip \
        python3-devel \
        which

RUN \
    ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip \
    && pip install --upgrade pip \
    && pip install pipenv \
    && dnf clean all

COPY . /app
WORKDIR /app

RUN pipenv install --system --deploy

VOLUME /app
ENTRYPOINT ["/app/entrypoint.sh"]
