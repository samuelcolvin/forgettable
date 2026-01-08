package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/riandyrn/otelchi"
)

func main() {
	cfg := LoadConfig()

	// Initialize OpenTelemetry
	ctx := context.Background()
	shutdown, err := InitTracer(ctx)
	if err != nil {
		log.Fatalf("Failed to initialize tracer: %v", err)
	}
	defer func() {
		if err := shutdown(ctx); err != nil {
			log.Printf("Error shutting down tracer: %v", err)
		}
	}()

	// Initialize clients
	pythonClient := NewPythonAgentClient(cfg.PythonAgentURL)
	dbClient := NewRustDBClient(cfg.RustDBURL)
	storage := NewStorage(dbClient)

	// Initialize handlers
	h := NewHandlers(pythonClient, storage)

	// Setup router
	r := chi.NewRouter()

	// Middleware
	r.Use(otelchi.Middleware("go-main", otelchi.WithChiRoutes(r)))
	r.Use(HeaderCaptureMiddleware)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(120 * time.Second))
	r.Use(middleware.RealIP)
	r.Use(middleware.RequestID)

	// Routes
	r.Get("/", h.HandleRoot)
	r.Get("/health", h.HandleHealth)

	// Project routes
	r.Route("/{uuid}", func(r chi.Router) {
		r.Get("/", h.HandleProject)
		r.Post("/create", h.HandleCreate)
		r.Post("/edit", h.HandleEdit)
		r.Get("/view", h.HandleView)
		r.Get("/view/assets/*", h.HandleAsset)
	})

	// Start server
	addr := fmt.Sprintf(":%d", cfg.Port)
	log.Printf("Starting server on %s", addr)
	log.Printf("Python Agent URL: %s", cfg.PythonAgentURL)
	log.Printf("Rust DB URL: %s", cfg.RustDBURL)

	srv := &http.Server{
		Addr:         addr,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 130 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Graceful shutdown
	go func() {
		if err := srv.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server stopped")
}
