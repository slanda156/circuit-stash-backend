FROM python:3.13-slim

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY main.py /app/main.py
COPY src /app/src
COPY logger.template.yaml /app/logger.template.yaml
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod ug+x /app/main.py
RUN chmod -R ug+x /app/src/
RUN chmod ug+x /app/entrypoint.sh
RUN apt-get update && apt-get install -y

WORKDIR /app

EXPOSE 8000

CMD ["/app/entrypoint.sh"]