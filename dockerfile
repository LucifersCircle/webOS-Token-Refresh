FROM python:3.10-slim

WORKDIR /usr/src/app

RUN adduser --disabled-password --gecos '' appuser

COPY . .
RUN pip install --no-cache-dir flask requests cryptography


RUN chown -R appuser:appuser /usr/src/app

USER appuser

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
