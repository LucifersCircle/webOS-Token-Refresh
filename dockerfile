FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos "" appuser

COPY . .

RUN chown -R appuser:appuser /usr/src/app

RUN pip install --no-cache-dir flask requests cryptography gunicorn

USER appuser

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
