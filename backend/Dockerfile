FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -o /out/server ./cmd/server
RUN CGO_ENABLED=0 go build -trimpath -o /out/seeder ./cmd/seeder

FROM alpine:3.22
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=build /out/server /out/seeder ./
COPY migrations ./migrations
COPY scripts ./scripts
USER app
EXPOSE 8080
ENTRYPOINT ["/app/server"]
