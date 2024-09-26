FROM public.ecr.aws/docker/library/golang:1.23.0-bullseye AS builder

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download
RUN go mod tidy

COPY . .

RUN make build

FROM debian:bullseye-slim AS runner

WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
