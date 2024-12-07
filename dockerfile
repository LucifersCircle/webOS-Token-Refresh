FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos '' appuser

COPY . .

RUN chown -R appuser:appuser /usr/src/app

RUN pip install --no-cache-dir flask requests cryptography

USER appuser

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "app.py"]
