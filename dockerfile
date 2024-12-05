FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos '' appuser
USER appuser

RUN chown -R appuser /usr/src/appuser

COPY . .

RUN pip install --no-cache-dir flask requests cryptography

CMD ["flask", "run", "--host=0.0.0.0"]
