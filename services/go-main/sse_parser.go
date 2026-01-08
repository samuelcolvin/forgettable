package main

import (
	"bufio"
	"encoding/json"
	"io"
	"maps"
	"strings"
)

// SSEEvent represents a parsed SSE event from pydantic-ai's VercelAIAdapter.
type SSEEvent struct {
	Type           string `json:"type"`
	ToolCallID     string `json:"toolCallId,omitempty"`
	ToolName       string `json:"toolName,omitempty"`
	InputTextDelta string `json:"inputTextDelta,omitempty"`
	Output         string `json:"output,omitempty"`
	FinishReason   string `json:"finishReason,omitempty"`
	Delta          string `json:"delta,omitempty"`
	ID             string `json:"id,omitempty"`
}

// CreateFileArgs represents the arguments for create_file tool.
type CreateFileArgs struct {
	FilePath string `json:"file_path"`
	Content  string `json:"content"`
}

// EditFileArgs represents the arguments for edit_file tool.
type EditFileArgs struct {
	FilePath string   `json:"file_path"`
	Diff     DiffArgs `json:"diff"`
}

// DiffArgs represents the diff structure for edit_file.
type DiffArgs struct {
	Hunks []DiffHunkArgs `json:"hunks"`
}

// DiffHunkArgs represents a single hunk in a diff.
type DiffHunkArgs struct {
	Search  string `json:"search"`
	Replace string `json:"replace"`
}

// DeleteFileArgs represents the arguments for delete_file tool.
type DeleteFileArgs struct {
	FilePath string `json:"file_path"`
}

// FileOperation represents a file operation extracted from the stream.
type FileOperation struct {
	Type     string // "create", "edit", "delete"
	FilePath string
	Content  string    // For create - the full file content
	Diff     *DiffArgs // For edit
}

// pendingToolCall tracks a tool call in progress.
type pendingToolCall struct {
	toolName  string
	inputJSON strings.Builder
}

// SSEParser parses SSE events from pydantic-ai's VercelAIAdapter.
type SSEParser struct {
	reader       *bufio.Reader
	files        map[string]string           // Track current file state
	pendingCalls map[string]*pendingToolCall // Track in-progress tool calls by ID
}

// NewSSEParser creates a new SSE parser.
func NewSSEParser(r io.Reader, initialFiles map[string]string) *SSEParser {
	files := make(map[string]string)
	maps.Copy(files, initialFiles)
	return &SSEParser{
		reader:       bufio.NewReader(r),
		files:        files,
		pendingCalls: make(map[string]*pendingToolCall),
	}
}

// ParsedEvent represents a parsed SSE event with extracted information.
type ParsedEvent struct {
	RawLine    string
	FileOp     *FileOperation
	IsFinished bool
}

// ReadEvent reads and parses the next event from the stream.
func (p *SSEParser) ReadEvent() (*ParsedEvent, error) {
	line, err := p.reader.ReadString('\n')
	if err != nil {
		return nil, err
	}

	result := &ParsedEvent{RawLine: line}

	// SSE format: "data: {json}\n"
	line = strings.TrimSpace(line)
	if !strings.HasPrefix(line, "data: ") {
		return result, nil
	}

	jsonData := strings.TrimPrefix(line, "data: ")
	if jsonData == "" {
		return result, nil
	}

	var event SSEEvent
	if err := json.Unmarshal([]byte(jsonData), &event); err != nil {
		return result, nil
	}

	switch event.Type {
	case "tool-input-start":
		// Start tracking a new tool call
		p.pendingCalls[event.ToolCallID] = &pendingToolCall{
			toolName: event.ToolName,
		}

	case "tool-input-delta":
		// Accumulate input JSON
		if pending, ok := p.pendingCalls[event.ToolCallID]; ok {
			pending.inputJSON.WriteString(event.InputTextDelta)
		}

	case "tool-output-available":
		// Tool completed - extract file operation
		if pending, ok := p.pendingCalls[event.ToolCallID]; ok {
			result.FileOp = p.extractFileOperation(pending.toolName, pending.inputJSON.String())
			delete(p.pendingCalls, event.ToolCallID)
		}

	case "finish":
		result.IsFinished = true
	}

	return result, nil
}

// extractFileOperation parses tool input and extracts file operation.
func (p *SSEParser) extractFileOperation(toolName, inputJSON string) *FileOperation {
	switch toolName {
	case "create_file":
		var args CreateFileArgs
		if err := json.Unmarshal([]byte(inputJSON), &args); err != nil {
			return nil
		}
		// Update tracked file state
		p.files[args.FilePath] = args.Content
		return &FileOperation{
			Type:     "create",
			FilePath: args.FilePath,
			Content:  args.Content,
		}

	case "edit_file":
		var args EditFileArgs
		if err := json.Unmarshal([]byte(inputJSON), &args); err != nil {
			return nil
		}
		// Apply diff to tracked file state
		if content, ok := p.files[args.FilePath]; ok {
			newContent := content
			for _, hunk := range args.Diff.Hunks {
				newContent = strings.Replace(newContent, hunk.Search, hunk.Replace, 1)
			}
			p.files[args.FilePath] = newContent
		}
		return &FileOperation{
			Type:     "edit",
			FilePath: args.FilePath,
			Diff:     &args.Diff,
		}

	case "delete_file":
		var args DeleteFileArgs
		if err := json.Unmarshal([]byte(inputJSON), &args); err != nil {
			return nil
		}
		delete(p.files, args.FilePath)
		return &FileOperation{
			Type:     "delete",
			FilePath: args.FilePath,
		}
	}

	return nil
}

// GetFiles returns the current state of all files.
func (p *SSEParser) GetFiles() map[string]string {
	result := make(map[string]string)
	maps.Copy(result, p.files)
	return result
}
