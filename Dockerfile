FROM python:3.9-slim

WORKDIR /app
RUN mkdir -p data/services/
COPY src/*.py /app/
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y cron
RUN pip install --no-cache-dir -r requirements.txt

COPY src/run.sh /app/
RUN chmod +x /app/run.sh
COPY src/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
# CMD /app/run.sh
