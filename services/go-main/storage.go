package main

import (
	"context"
	"encoding/json"
	"path/filepath"
	"strings"
	"time"
)

// Storage provides a high-level interface over the Rust DB client.
type Storage struct {
	client *RustDBClient
}

// NewStorage creates a new Storage instance.
func NewStorage(client *RustDBClient) *Storage {
	return &Storage{client: client}
}

// AppMetadata contains metadata about a stored app.
type AppMetadata struct {
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
	Summary       string    `json:"summary"`
	SourceFiles   []string  `json:"source_files"`
	CompiledFiles []string  `json:"compiled_files"`
}

// StoreApp saves all app files and metadata to the database.
func (s *Storage) StoreApp(ctx context.Context, projectID string, files, compiledFiles map[string]string, summary string) error {
	sourceFileList := make([]string, 0, len(files))
	compiledFileList := make([]string, 0, len(compiledFiles))

	// Store source files
	for path, content := range files {
		key := "source/" + path
		mimeType := getMimeType(path)
		if err := s.client.Store(ctx, projectID, key, mimeType, []byte(content)); err != nil {
			return err
		}
		sourceFileList = append(sourceFileList, path)
	}

	// Store compiled files
	for path, content := range compiledFiles {
		key := "compiled/" + path
		mimeType := getMimeType(path)
		if err := s.client.Store(ctx, projectID, key, mimeType, []byte(content)); err != nil {
			return err
		}
		compiledFileList = append(compiledFileList, path)
	}

	// Store metadata
	now := time.Now().UTC()
	meta := AppMetadata{
		CreatedAt:     now,
		UpdatedAt:     now,
		Summary:       summary,
		SourceFiles:   sourceFileList,
		CompiledFiles: compiledFileList,
	}
	metaJSON, err := json.Marshal(meta)
	if err != nil {
		return err
	}
	return s.client.Store(ctx, projectID, "_meta/app.json", "application/json", metaJSON)
}

// UpdateApp updates existing app files and metadata.
func (s *Storage) UpdateApp(ctx context.Context, projectID string, files, compiledFiles map[string]string, summary string) error {
	// Delete old compiled files first
	oldCompiled, err := s.client.List(ctx, projectID, "compiled/")
	if err == nil {
		for _, entry := range oldCompiled {
			_ = s.client.Delete(ctx, projectID, entry.Key)
		}
	}

	// Delete old source files
	oldSource, err := s.client.List(ctx, projectID, "source/")
	if err == nil {
		for _, entry := range oldSource {
			_ = s.client.Delete(ctx, projectID, entry.Key)
		}
	}

	// Get existing metadata for created_at timestamp
	var createdAt time.Time
	existingMeta, err := s.GetMetadata(ctx, projectID)
	if err == nil {
		createdAt = existingMeta.CreatedAt
	} else {
		createdAt = time.Now().UTC()
	}

	sourceFileList := make([]string, 0, len(files))
	compiledFileList := make([]string, 0, len(compiledFiles))

	// Store new source files
	for path, content := range files {
		key := "source/" + path
		mimeType := getMimeType(path)
		if storeErr := s.client.Store(ctx, projectID, key, mimeType, []byte(content)); storeErr != nil {
			return storeErr
		}
		sourceFileList = append(sourceFileList, path)
	}

	// Store new compiled files
	for path, content := range compiledFiles {
		key := "compiled/" + path
		mimeType := getMimeType(path)
		if storeErr := s.client.Store(ctx, projectID, key, mimeType, []byte(content)); storeErr != nil {
			return storeErr
		}
		compiledFileList = append(compiledFileList, path)
	}

	// Update metadata
	meta := AppMetadata{
		CreatedAt:     createdAt,
		UpdatedAt:     time.Now().UTC(),
		Summary:       summary,
		SourceFiles:   sourceFileList,
		CompiledFiles: compiledFileList,
	}
	metaJSON, err := json.Marshal(meta)
	if err != nil {
		return err
	}
	return s.client.Store(ctx, projectID, "_meta/app.json", "application/json", metaJSON)
}

// GetSourceFiles retrieves all source files for a project.
func (s *Storage) GetSourceFiles(ctx context.Context, projectID string) (map[string]string, error) {
	entries, err := s.client.List(ctx, projectID, "source/")
	if err != nil {
		return nil, err
	}

	files := make(map[string]string)
	for _, entry := range entries {
		content, _, err := s.client.Get(ctx, projectID, entry.Key)
		if err != nil {
			return nil, err
		}
		path := strings.TrimPrefix(entry.Key, "source/")
		files[path] = string(content)
	}
	return files, nil
}

// GetCompiledFile retrieves a single compiled file.
func (s *Storage) GetCompiledFile(ctx context.Context, projectID, path string) ([]byte, string, error) {
	key := "compiled/" + path
	return s.client.Get(ctx, projectID, key)
}

// GetMetadata retrieves the app metadata.
func (s *Storage) GetMetadata(ctx context.Context, projectID string) (*AppMetadata, error) {
	content, _, err := s.client.Get(ctx, projectID, "_meta/app.json")
	if err != nil {
		return nil, err
	}

	var meta AppMetadata
	if err := json.Unmarshal(content, &meta); err != nil {
		return nil, err
	}
	return &meta, nil
}

// HasApp checks if an app exists for the project.
func (s *Storage) HasApp(ctx context.Context, projectID string) bool {
	_, err := s.GetMetadata(ctx, projectID)
	return err == nil
}

// getMimeType returns the MIME type for a file path.
func getMimeType(path string) string {
	ext := strings.ToLower(filepath.Ext(path))
	switch ext {
	case ".html":
		return "text/html"
	case ".css":
		return "text/css"
	case ".js":
		return "application/javascript"
	case ".ts", ".tsx":
		return "text/typescript"
	case ".json":
		return "application/json"
	case ".map":
		return "application/json"
	case ".svg":
		return "image/svg+xml"
	case ".png":
		return "image/png"
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".gif":
		return "image/gif"
	case ".woff":
		return "font/woff"
	case ".woff2":
		return "font/woff2"
	default:
		return "application/octet-stream"
	}
}
