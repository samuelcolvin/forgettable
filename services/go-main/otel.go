package main

import (
	"context"
	"net/http"
	"os"
	"strings"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.37.0"
	oteltrace "go.opentelemetry.io/otel/trace"
)

// InitTracer initializes the OpenTelemetry tracer provider for Logfire.
// Returns a shutdown function that should be called when the application exits.
func InitTracer(ctx context.Context) (func(context.Context) error, error) {
	token := os.Getenv("LOGFIRE_TOKEN")
	if token == "" {
		// Return no-op shutdown if no token configured
		return func(context.Context) error { return nil }, nil
	}

	// Create OTLP HTTP exporter for Logfire
	exporter, err := otlptracehttp.New(ctx,
		otlptracehttp.WithEndpoint("logfire-us.pydantic.dev"),
		otlptracehttp.WithHeaders(map[string]string{
			"Authorization": token,
		}),
	)
	if err != nil {
		return nil, err
	}

	// Create resource with service name
	res, err := resource.Merge(
		resource.Default(),
		resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("go-main"),
		),
	)
	if err != nil {
		return nil, err
	}

	// Create tracer provider
	tp := trace.NewTracerProvider(
		trace.WithBatcher(exporter),
		trace.WithResource(res),
	)

	// Set global tracer provider and propagator
	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	return tp.Shutdown, nil
}

// HeaderCaptureMiddleware captures HTTP request headers as span attributes.
func HeaderCaptureMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		span := oteltrace.SpanFromContext(r.Context())
		if span.IsRecording() {
			for name, values := range r.Header {
				attrName := "http.request.header." + strings.ToLower(strings.ReplaceAll(name, "-", "_"))
				span.SetAttributes(attribute.StringSlice(attrName, values))
			}
		}
		next.ServeHTTP(w, r)
	})
}
