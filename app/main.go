package main

import (
	"encoding/json"
	"log/slog"
	"strconv"

	"github.com/labstack/echo/v4"
)

func Add(a int, b int) int {
	return a + b
}

func main() {
	e := echo.New()
	e.GET("/", func(c echo.Context) error {
		slog.Info("Access route health check")

		return json.NewEncoder(c.Response()).Encode(map[string]string{"message": "hello world okoko STL"})
	})

	e.POST("/add", func(c echo.Context) error {
		slog.Info("Access route add api")

		a, error := strconv.Atoi(c.Request().FormValue("a"))
		if error != nil {
			return c.JSON(400, map[string]string{"error": "a is not a number"})
		}

		b, error := strconv.Atoi(c.Request().FormValue("b"))
		if error != nil {
			return c.JSON(400, map[string]string{"error": "b is not a number"})
		}

		return json.NewEncoder(c.Response()).Encode(map[string]int{"result": Add(a, b)})
	})
	e.Logger.Fatal(e.Start(":8080"))
}
