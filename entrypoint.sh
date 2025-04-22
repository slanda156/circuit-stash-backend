#!/bin/bash

python3 -c "
import os

with open('/app/logger.template.yaml') as f:
    template = f.read()

output = template.replace('\${LOG_LEVEL}', os.getenv('LOG_LEVEL', 'INFO'))

with open('/app/logger.yaml', 'w') as f:
    f.write(output)
"

rm -f /app/logger.template.yaml
exec python main.py
