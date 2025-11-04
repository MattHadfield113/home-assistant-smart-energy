ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.19
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-aiohttp \
    py3-flask \
    bash

# Copy data for add-on
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY app /app
COPY run.sh /
RUN chmod a+x /run.sh

WORKDIR /app

# Start the application
CMD ["/run.sh"]
