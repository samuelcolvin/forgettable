package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

var httpClient = &http.Client{
	Timeout: 120 * time.Second,
	Transport: otelhttp.NewTransport(&http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     90 * time.Second,
	}),
}

// PythonAgentClient handles communication with the Python Agent service.
type PythonAgentClient struct {
	baseURL string
}

// NewPythonAgentClient creates a new Python Agent client.
func NewPythonAgentClient(baseURL string) *PythonAgentClient {
	return &PythonAgentClient{baseURL: baseURL}
}

// CreateAppRequest is the request body for creating an app.
type CreateAppRequest struct {
	Prompt string `json:"prompt"`
}

// CreateAppResponse is the response from creating an app.
type CreateAppResponse struct {
	Files         map[string]string `json:"files"`
	CompiledFiles map[string]string `json:"compiled_files"`
	Summary       string            `json:"summary"`
}

// EditAppRequest is the request body for editing an app.
type EditAppRequest struct {
	Prompt string            `json:"prompt"`
	Files  map[string]string `json:"files"`
}

// DiffHunk represents a single search/replace operation.
type DiffHunk struct {
	Search  string `json:"search"`
	Replace string `json:"replace"`
}

// Diff represents changes to a file.
type Diff struct {
	Hunks []DiffHunk `json:"hunks"`
}

// EditAppResponse is the response from editing an app.
type EditAppResponse struct {
	Diffs         map[string]Diff   `json:"diffs"`
	Files         map[string]string `json:"files"`
	CompiledFiles map[string]string `json:"compiled_files"`
	Summary       string            `json:"summary"`
}

// CreateApp sends a create request to the Python Agent.
func (c *PythonAgentClient) CreateApp(ctx context.Context, prompt string) (*CreateAppResponse, error) {
	reqBody := CreateAppRequest{Prompt: prompt}
	body, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/apps", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("python agent request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("python agent error (%d): %s", resp.StatusCode, respBody)
	}

	var result CreateAppResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// EditApp sends an edit request to the Python Agent.
func (c *PythonAgentClient) EditApp(ctx context.Context, prompt string, files map[string]string) (*EditAppResponse, error) {
	reqBody := EditAppRequest{Prompt: prompt, Files: files}
	body, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/apps/edit", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("python agent request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("python agent error (%d): %s", resp.StatusCode, respBody)
	}

	var result EditAppResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// RustDBClient handles communication with the Rust DB service.
type RustDBClient struct {
	baseURL string
}

// NewRustDBClient creates a new Rust DB client.
func NewRustDBClient(baseURL string) *RustDBClient {
	return &RustDBClient{baseURL: baseURL}
}

// KeyInfo represents an entry in the list response.
type KeyInfo struct {
	Key      string `json:"key"`
	MimeType string `json:"mime_type"`
}

// Store saves content to the Rust DB.
func (c *RustDBClient) Store(ctx context.Context, project, key, mimeType string, content []byte) error {
	reqURL := fmt.Sprintf("%s/project/%s/%s", c.baseURL, project, url.PathEscape(key))
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, reqURL, bytes.NewReader(content))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", mimeType)

	resp, err := httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("rust db request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusCreated {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("store failed (%d): %s", resp.StatusCode, respBody)
	}
	return nil
}

// Get retrieves content from the Rust DB.
func (c *RustDBClient) Get(ctx context.Context, project, key string) ([]byte, string, error) {
	reqURL := fmt.Sprintf("%s/project/%s/get/%s", c.baseURL, project, url.PathEscape(key))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, reqURL, nil)
	if err != nil {
		return nil, "", fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, "", fmt.Errorf("rust db request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode == http.StatusNotFound {
		return nil, "", ErrNotFound
	}
	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, "", fmt.Errorf("get failed (%d): %s", resp.StatusCode, respBody)
	}

	content, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, "", fmt.Errorf("failed to read response: %w", err)
	}

	mimeType := resp.Header.Get("Content-Type")
	return content, mimeType, nil
}

// List retrieves all keys with a given prefix from the Rust DB.
func (c *RustDBClient) List(ctx context.Context, project, prefix string) ([]KeyInfo, error) {
	reqURL := fmt.Sprintf("%s/project/%s/list/%s", c.baseURL, project, url.PathEscape(prefix))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, reqURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("rust db request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("list failed (%d): %s", resp.StatusCode, respBody)
	}

	var result []KeyInfo
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return result, nil
}

// Delete removes a key from the Rust DB.
func (c *RustDBClient) Delete(ctx context.Context, project, key string) error {
	reqURL := fmt.Sprintf("%s/project/%s/%s", c.baseURL, project, url.PathEscape(key))
	req, err := http.NewRequestWithContext(ctx, http.MethodDelete, reqURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("rust db request failed: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusNoContent && resp.StatusCode != http.StatusNotFound {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("delete failed (%d): %s", resp.StatusCode, respBody)
	}
	return nil
}
