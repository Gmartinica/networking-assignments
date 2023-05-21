FROM python:latest

WORKDIR /client

COPY . .

CMD python -u httpc.py post router:3000 -h Content-Type:application/json --d '{"Assignment": 1}'
