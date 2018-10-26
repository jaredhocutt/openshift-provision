FROM quay.io/jhocutt/openshift-provision-base:latest

ENV PYCURL_SSL_LIBRARY=openssl

WORKDIR /app

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system --deploy

COPY . /app

ENTRYPOINT ["/app/entrypoint.sh"]
