import { forwardRef, useImperativeHandle, useRef, useState } from 'react'

import { cn } from '@/lib/utils'

export interface PreviewPaneRef {
  refresh: () => void
}

interface PreviewPaneProps {
  projectId: string
  className?: string
}

export const PreviewPane = forwardRef<PreviewPaneRef, PreviewPaneProps>(({ projectId, className }, ref) => {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [hasError, setHasError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useImperativeHandle(ref, () => ({
    refresh: () => {
      setIsLoading(true)
      setHasError(false)
      setRefreshKey((k) => k + 1)
    },
  }))

  const handleLoad = () => {
    setIsLoading(false)
  }

  const handleError = () => {
    setIsLoading(false)
    setHasError(true)
  }

  const previewUrl = `/api/${projectId}/view?t=${refreshKey}`

  return (
    <div className={cn('relative h-full w-full bg-muted/30', className)}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <div className="size-8 animate-spin rounded-full border-2 border-current border-t-transparent" />
            <span className="text-sm">Loading preview...</span>
          </div>
        </div>
      )}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <span className="text-sm">No app generated yet</span>
            <span className="text-xs">Start a conversation to generate your app</span>
          </div>
        </div>
      )}
      <iframe
        ref={iframeRef}
        key={refreshKey}
        src={previewUrl}
        className="h-full w-full border-0"
        title="App Preview"
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  )
})

PreviewPane.displayName = 'PreviewPane'
