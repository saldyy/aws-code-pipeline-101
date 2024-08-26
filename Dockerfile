FROM golang:1.22.6-bullseye as builder

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download
RUN go mod tidy

COPY . .

RUN go build -o main ./main.go

FROM debian:bullseye-slim

WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
