FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos "" appuser

COPY . .

RUN chown -R appuser:appuser /usr/src/app

RUN pip install --no-cache-dir flask requests cryptography gunicorn

USER appuser

# Environment variable to specify the app script
ENV APP_SCRIPT="app:app"

CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:5000 $APP_SCRIPT"]