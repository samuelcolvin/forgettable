import { type UIMessage } from 'ai'
import { useCallback, useEffect, useRef, useState } from 'react'
import { PreviewPane, type PreviewPaneRef } from '@/components/preview-pane'
import { ThemeProvider } from '@/components/theme-provider'
import { Chat } from './Chat'

interface ProjectState {
  hasApp: boolean
  conversation?: UIMessage[]
  metadata?: {
    summary?: string
    sourceFiles?: string[]
    compiledFiles?: string[]
  }
}

function generateUuid(): string {
  return crypto.randomUUID()
}

function getProjectIdFromPath(): string | null {
  const path = window.location.pathname
  const match = path.match(/^\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i)
  return match?.[1] ?? null
}

function App() {
  const previewRef = useRef<PreviewPaneRef>(null)
  const [projectId, setProjectId] = useState<string | null>(getProjectIdFromPath)
  const [initialState, setInitialState] = useState<ProjectState | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Redirect to a new UUID if none in path
  useEffect(() => {
    if (!projectId) {
      const newId = generateUuid()
      window.history.replaceState(null, '', `/${newId}`)
      setProjectId(newId)
    }
  }, [projectId])

  // Fetch initial state on mount
  useEffect(() => {
    if (!projectId) return

    async function fetchState() {
      try {
        const response = await fetch(`/api/${projectId}/state`)
        if (response.ok) {
          const data = await response.json()
          setInitialState(data)
        } else {
          setInitialState({ hasApp: false })
        }
      } catch (err) {
        console.error('Failed to fetch project state:', err)
        setInitialState({ hasApp: false })
      } finally {
        setIsLoading(false)
      }
    }

    fetchState()
  }, [projectId])

  const handleFileChange = useCallback(() => {
    // Small delay to allow the server to process the file changes
    setTimeout(() => {
      previewRef.current?.refresh()
    }, 500)
  }, [])

  // Show loading while fetching initial state
  if (!projectId || isLoading) {
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
          <PreviewPane ref={previewRef} projectId={projectId} initialHasApp={initialState?.hasApp ?? false} />
        </div>

        {/* Chat pane - 1/3 width */}
        <div className="flex-1 flex flex-col min-w-[300px]">
          <Chat projectId={projectId} onFileChange={handleFileChange} initialMessages={initialState?.conversation} />
        </div>
      </div>
    </ThemeProvider>
  )
}

export default App
