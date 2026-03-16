FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir requests htmldom google-genai

COPY main.py .

CMD ["sleep", "infinity"]
