FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos '' appuser

COPY . .

RUN chown -R appuser:appuser /usr/src/app

RUN pip install --no-cache-dir flask requests cryptography

USER appuser

# Use an environment variable to decide which script to run
ENV APP_SCRIPT="app.py"
CMD ["sh", "-c", "python $APP_SCRIPT"]
