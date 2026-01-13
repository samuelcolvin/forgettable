package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"regexp"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
)

// AppError represents an application error with HTTP status code.
type AppError struct {
	Code    int    `json:"-"`
	Message string `json:"error"`
}

func (e AppError) Error() string {
	return e.Message
}

// Common errors.
var (
	ErrNotFound       = AppError{Code: http.StatusNotFound, Message: "Not found"}
	ErrInvalidRequest = AppError{Code: http.StatusBadRequest, Message: "Invalid request"}
	ErrInvalidUUID    = AppError{Code: http.StatusBadRequest, Message: "Invalid project ID"}
)

// Handlers contains HTTP handlers and their dependencies.
type Handlers struct {
	pythonClient    *PythonAgentClient
	nodeBuildClient *NodeBuildClient
	storage         *Storage
}

// NewHandlers creates a new Handlers instance.
func NewHandlers(pythonClient *PythonAgentClient, nodeBuildClient *NodeBuildClient, storage *Storage) *Handlers {
	return &Handlers{
		pythonClient:    pythonClient,
		nodeBuildClient: nodeBuildClient,
		storage:         storage,
	}
}

// writeError writes an error response as JSON.
func writeError(w http.ResponseWriter, err error) {
	var appErr AppError
	if errors.As(err, &appErr) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(appErr.Code)
		_ = json.NewEncoder(w).Encode(appErr)
		return
	}
	log.Printf("unexpected error: %v", err)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)
	_ = json.NewEncoder(w).Encode(AppError{Message: "Internal server error"})
}

// writeJSON writes a JSON response.
func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}

// validateUUID validates that the given string is a valid UUID.
func validateUUID(id string) error {
	if _, err := uuid.Parse(id); err != nil {
		return ErrInvalidUUID
	}
	return nil
}

// HandleHealth returns a health check response.
func (h *Handlers) HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("OK"))
}

// CreateRequest is the request body for creating an app.
type CreateRequest struct {
	Prompt string `json:"prompt"`
}

// CreateResponse is the response for creating an app.
type CreateResponse struct {
	Summary string   `json:"summary"`
	Files   []string `json:"files"`
	ViewURL string   `json:"view_url"`
}

// HandleCreate creates a new app.
func (h *Handlers) HandleCreate(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	var req CreateRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Invalid JSON"})
		return
	}

	if req.Prompt == "" {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Prompt is required"})
		return
	}

	// Call Python Agent
	result, err := h.pythonClient.CreateApp(r.Context(), req.Prompt)
	if err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to create app: %v", err)})
		return
	}

	// Store in Rust DB
	if err := h.storage.StoreApp(r.Context(), projectID, result.Files, result.CompiledFiles, result.Summary); err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to store app: %v", err)})
		return
	}

	// Build response
	fileList := make([]string, 0, len(result.Files))
	for path := range result.Files {
		fileList = append(fileList, path)
	}

	resp := CreateResponse{
		Summary: result.Summary,
		Files:   fileList,
		ViewURL: "/" + projectID + "/view",
	}

	writeJSON(w, http.StatusOK, resp)
}

// EditRequest is the request body for editing an app.
type EditRequest struct {
	Prompt string `json:"prompt"`
}

// EditResponse is the response for editing an app.
type EditResponse struct {
	Summary string   `json:"summary"`
	Files   []string `json:"files"`
	ViewURL string   `json:"view_url"`
}

// HandleEdit edits an existing app.
func (h *Handlers) HandleEdit(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	var req EditRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Invalid JSON"})
		return
	}

	if req.Prompt == "" {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Prompt is required"})
		return
	}

	// Get existing source files
	existingFiles, err := h.storage.GetSourceFiles(r.Context(), projectID)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			writeError(w, AppError{Code: http.StatusNotFound, Message: "No app exists for this project"})
			return
		}
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to get existing files: %v", err)})
		return
	}

	if len(existingFiles) == 0 {
		writeError(w, AppError{Code: http.StatusNotFound, Message: "No app exists for this project"})
		return
	}

	// Call Python Agent
	result, err := h.pythonClient.EditApp(r.Context(), req.Prompt, existingFiles)
	if err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to edit app: %v", err)})
		return
	}

	// Update in Rust DB
	if err := h.storage.UpdateApp(r.Context(), projectID, result.Files, result.CompiledFiles, result.Summary); err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to update app: %v", err)})
		return
	}

	// Build response
	fileList := make([]string, 0, len(result.Files))
	for path := range result.Files {
		fileList = append(fileList, path)
	}

	resp := EditResponse{
		Summary: result.Summary,
		Files:   fileList,
		ViewURL: "/" + projectID + "/view",
	}

	writeJSON(w, http.StatusOK, resp)
}

// HandleView serves the generated app's index.html.
func (h *Handlers) HandleView(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	content, mimeType, err := h.storage.GetCompiledFile(r.Context(), projectID, "index.html")
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			w.WriteHeader(http.StatusNotFound)
			_, _ = w.Write([]byte("No app generated yet"))
			return
		}
		writeError(w, err)
		return
	}

	// Rewrite asset paths to go through our service
	html := string(content)
	html = rewriteAssetPaths(html, projectID)

	w.Header().Set("Content-Type", mimeType)
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(html))
}

// HandleAsset serves compiled assets.
func (h *Handlers) HandleAsset(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	// Get the asset path from the wildcard
	assetPath := chi.URLParam(r, "*")
	if assetPath == "" {
		writeError(w, ErrNotFound)
		return
	}

	// Prepend "assets/" to match the storage key structure
	fullPath := "assets/" + assetPath

	content, mimeType, err := h.storage.GetCompiledFile(r.Context(), projectID, fullPath)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			w.WriteHeader(http.StatusNotFound)
			_, _ = w.Write([]byte("Asset not found"))
			return
		}
		writeError(w, err)
		return
	}

	// Set caching headers for hashed assets
	w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
	w.Header().Set("Content-Type", mimeType)
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(content)
}

// HandleChat proxies chat requests to the Python Agent using Server-Sent Events.
// It intercepts the stream to extract file operations and stores them to rust-db.
func (h *Handlers) HandleChat(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	// Get existing source files to provide context
	existingFiles, err := h.storage.GetSourceFiles(r.Context(), projectID)
	if err != nil && !errors.Is(err, ErrNotFound) {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to get existing files: %v", err)})
		return
	}
	if existingFiles == nil {
		existingFiles = make(map[string]string)
	}

	// Read the original request body
	originalBody, err := io.ReadAll(r.Body)
	if err != nil {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Failed to read request body"})
		return
	}

	// Parse the original body to add files
	var bodyData map[string]any
	if unmarshalErr := json.Unmarshal(originalBody, &bodyData); unmarshalErr != nil {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Invalid JSON in request body"})
		return
	}

	// Add existing files to the request
	bodyData["files"] = existingFiles

	// Marshal the modified body
	modifiedBody, err := json.Marshal(bodyData)
	if err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: "Failed to serialize request body"})
		return
	}

	// Create request to Python Agent
	chatURL := h.pythonClient.baseURL + "/chat"
	proxyReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, chatURL, bytes.NewReader(modifiedBody))
	if err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: "Failed to create proxy request"})
		return
	}

	// Copy relevant headers
	proxyReq.Header.Set("Content-Type", "application/json")
	if accept := r.Header.Get("Accept"); accept != "" {
		proxyReq.Header.Set("Accept", accept)
	}

	// Make the request with a longer timeout for streaming
	client := &http.Client{Timeout: 0} // No timeout for streaming
	resp, err := client.Do(proxyReq)
	if err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to connect to chat service: %v", err)})
		return
	}
	defer func() { _ = resp.Body.Close() }()

	// Set SSE headers
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no") // Disable nginx buffering

	// Get the flusher for streaming
	flusher, ok := w.(http.Flusher)
	if !ok {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: "Streaming not supported"})
		return
	}

	w.WriteHeader(resp.StatusCode)

	// Create SSE parser to intercept file operations
	parser := NewSSEParser(resp.Body, existingFiles)
	var hadFileOps bool

	// Stream and parse events
	for {
		event, readErr := parser.ReadEvent()
		if readErr != nil {
			if readErr != io.EOF {
				log.Printf("Error reading from Python Agent: %v", readErr)
			}
			break
		}

		// Write the raw event to the client
		if _, writeErr := w.Write([]byte(event.RawLine)); writeErr != nil {
			log.Printf("Error writing to client: %v", writeErr)
			return
		}
		flusher.Flush()

		// Process file operations
		if event.FileOp != nil {
			hadFileOps = true
			switch event.FileOp.Type {
			case "create", "edit":
				// Get the updated content from the parser's tracked state
				content := parser.GetFiles()[event.FileOp.FilePath]
				if storeErr := h.storage.StoreSourceFile(r.Context(), projectID, event.FileOp.FilePath, content); storeErr != nil {
					log.Printf("Error storing file %s: %v", event.FileOp.FilePath, storeErr)
				}
			case "delete":
				if delErr := h.storage.DeleteSourceFile(r.Context(), projectID, event.FileOp.FilePath); delErr != nil {
					log.Printf("Error deleting file %s: %v", event.FileOp.FilePath, delErr)
				}
			}
		}

		// On finish, trigger compilation if there were file operations
		// Run synchronously so the client knows the app is ready when the stream ends
		if event.IsFinished && hadFileOps {
			h.compileAndStore(projectID, parser.GetFiles())
		}
	}
}

// compileAndStore compiles source files and stores the compiled output.
func (h *Handlers) compileAndStore(projectID string, files map[string]string) {
	ctx := context.Background()

	// Compile via Node Build
	compiledFiles, err := h.nodeBuildClient.Build(ctx, files)
	if err != nil {
		log.Printf("Error compiling project %s: %v", projectID, err)
		return
	}

	// Store compiled files
	if err := h.storage.StoreCompiledFiles(ctx, projectID, compiledFiles); err != nil {
		log.Printf("Error storing compiled files for project %s: %v", projectID, err)
	}

	log.Printf("Successfully compiled and stored project %s", projectID)
}

// StateResponse is the response for the state endpoint.
type StateResponse struct {
	HasApp       bool            `json:"hasApp"`
	Conversation json.RawMessage `json:"conversation,omitempty"`
	Metadata     *AppMetadata    `json:"metadata,omitempty"`
}

// HandleGetState returns the current state of a project.
func (h *Handlers) HandleGetState(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	resp := StateResponse{
		HasApp: h.storage.HasApp(r.Context(), projectID),
	}

	// Try to get conversation
	conversation, err := h.storage.GetConversation(r.Context(), projectID)
	if err == nil {
		resp.Conversation = conversation
	}

	// Try to get metadata
	metadata, err := h.storage.GetMetadata(r.Context(), projectID)
	if err == nil {
		resp.Metadata = metadata
	}

	writeJSON(w, http.StatusOK, resp)
}

// SaveConversationRequest is the request body for saving conversation.
type SaveConversationRequest struct {
	Messages json.RawMessage `json:"messages"`
}

// HandleSaveConversation saves the conversation state.
func (h *Handlers) HandleSaveConversation(w http.ResponseWriter, r *http.Request) {
	projectID := chi.URLParam(r, "uuid")
	if err := validateUUID(projectID); err != nil {
		writeError(w, err)
		return
	}

	var req SaveConversationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, AppError{Code: http.StatusBadRequest, Message: "Invalid JSON"})
		return
	}

	if err := h.storage.StoreConversation(r.Context(), projectID, req.Messages); err != nil {
		writeError(w, AppError{Code: http.StatusInternalServerError, Message: fmt.Sprintf("Failed to store conversation: %v", err)})
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// rewriteAssetPaths rewrites asset paths in HTML to use relative paths.
// This ensures assets load correctly whether accessed directly or via proxy.
// When accessed via /api/{uuid}/view, relative paths like ./assets/ resolve
// to /api/{uuid}/view/assets/ which correctly goes through the proxy.
func rewriteAssetPaths(html, _ string) string {
	// Replace /assets/ with ./assets/ (relative path)
	re := regexp.MustCompile(`(src|href)=["'](/assets/)`)
	html = re.ReplaceAllString(html, `$1="./assets/`)

	// Also handle assets/ without leading / (already relative, just ensure ./ prefix)
	re2 := regexp.MustCompile(`(src|href)=["'](assets/)`)
	html = re2.ReplaceAllString(html, `$1="./assets/`)

	return html
}
