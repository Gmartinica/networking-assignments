FROM golang:latest

WORKDIR /router

COPY . .

RUN go build router.go

CMD [ "./router" ]