FROM python:3.11-alpine

WORKDIR /app
# Install necessary packages
RUN apk update && apk add --no-cache \
    chromium \
    chromium-chromedriver \
    && rm -rf /var/cache/apk/*

COPY . /app
# Install the required packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install .
ENV PYTHONPATH=/app/src
ENV UVICORN_PATH=/usr/local/bin/uvicorn
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD python3 run.py
