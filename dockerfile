FROM python:3.10-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir flask requests cryptography

CMD ["flask", "run", "--host=0.0.0.0"]
