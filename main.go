package main

import (
	"encoding/json"
	"log/slog"

	"github.com/labstack/echo/v4"
)

func main() {
	e := echo.New()
	e.GET("/", func(c echo.Context) error {
		slog.Info("Access route health check")

    return json.NewEncoder(c.Response()).Encode(map[string]string{"message": "ok"})
	})
	e.Logger.Fatal(e.Start(":8080"))
}
