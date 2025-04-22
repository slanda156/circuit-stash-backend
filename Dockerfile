FROM python:3.14-slim

# Copy requirements file and install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy application files
COPY main.py /app/main.py
COPY src /app/src
COPY logger.yaml /app/logger.yaml

RUN chmod ug+x /app/main.py
RUN chmod -R ug+x /app/src/
RUN apt-get update && apt-get install -y

WORKDIR /app

# Command to run the application
CMD ["python", "main.py"]