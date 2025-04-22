#!/bin/bash
envsubst "${LOG_LEVEL}" < /app/logger.template.yaml > /app/logger.yaml
rm -f /app/logger.template.yaml
exec python main.py