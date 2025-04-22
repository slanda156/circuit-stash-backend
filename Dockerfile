FROM python:3.13-slim

# Copy requirements file and install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy application files
COPY main.py /app/main.py
COPY src /app/src
COPY logger.template.yaml /app/logger.template.yaml
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod ug+x /app/main.py
RUN chmod -R ug+x /app/src/
RUN apt-get update && apt-get install -y

WORKDIR /app

EXPOSE 8000

# Command to run the application
# CMD ["python", "main.py"]
CMD ["/app/entrypoint.sh"]