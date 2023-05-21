FROM python:latest

WORKDIR /client

COPY . .

CMD python -u httpc.py post server:8080 -h Content-Type:application/json --d '{"Assignment": 1}'
