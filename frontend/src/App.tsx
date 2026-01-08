import { useCallback, useEffect, useRef, useState } from 'react'
import { PreviewPane, type PreviewPaneRef } from '@/components/preview-pane'
import { ThemeProvider } from '@/components/theme-provider'
import { Chat } from './Chat'

function generateUuid(): string {
  return crypto.randomUUID()
}

function getProjectIdFromPath(): string | null {
  // Match UUID pattern in path (e.g., /abc123-def456 -> abc123-def456)
  const path = window.location.pathname
  const match = path.match(/^\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i)
  return match?.[1] ?? null
}

function App() {
  const previewRef = useRef<PreviewPaneRef>(null)
  const [projectId, setProjectId] = useState<string | null>(getProjectIdFromPath)

  // Redirect to a new UUID if none in path
  useEffect(() => {
    if (!projectId) {
      const newId = generateUuid()
      window.history.replaceState(null, '', `/${newId}`)
      setProjectId(newId)
    }
  }, [projectId])

  const handleFileChange = useCallback(() => {
    // Small delay to allow the server to process the file changes
    setTimeout(() => {
      previewRef.current?.refresh()
    }, 500)
  }, [])

  // Show loading while redirecting
  if (!projectId) {
    return (
      <ThemeProvider defaultTheme="system" storageKey="forgettable-theme">
        <div className="flex h-screen items-center justify-center">
          <div className="text-muted-foreground">Loading...</div>
        </div>
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider defaultTheme="system" storageKey="forgettable-theme">
      <div className="flex h-screen">
        {/* Preview pane - 2/3 width */}
        <div className="flex-[2] border-r">
          <PreviewPane ref={previewRef} projectId={projectId} />
        </div>

        {/* Chat pane - 1/3 width */}
        <div className="flex-1 flex flex-col min-w-[300px]">
          <Chat projectId={projectId} onFileChange={handleFileChange} />
        </div>
      </div>
    </ThemeProvider>
  )
}

export default App
