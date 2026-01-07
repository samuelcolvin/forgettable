package main

import (
	"os"
	"strconv"
)

type Config struct {
	Port           int
	PythonAgentURL string
	RustDBURL      string
}

func LoadConfig() Config {
	return Config{
		Port:           getEnvInt("PORT", 3002),
		PythonAgentURL: getEnv("PYTHON_AGENT_URL", "http://localhost:8000"),
		RustDBURL:      getEnv("RUST_DB_URL", "http://localhost:3001"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
