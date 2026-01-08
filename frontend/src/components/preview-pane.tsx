import { forwardRef, useImperativeHandle, useState } from 'react'

import { cn } from '@/lib/utils'

export interface PreviewPaneRef {
  refresh: () => void
}

interface PreviewPaneProps {
  projectId: string
  className?: string
}

export const PreviewPane = forwardRef<PreviewPaneRef, PreviewPaneProps>(({ projectId, className }, ref) => {
  const [refreshKey, setRefreshKey] = useState(0)
  const [hasApp, setHasApp] = useState(false)

  useImperativeHandle(ref, () => ({
    refresh: () => {
      setHasApp(true)
      setRefreshKey((k) => k + 1)
    },
  }))

  const previewUrl = `/api/${projectId}/view?t=${refreshKey}`

  return (
    <div className={cn('relative h-full w-full bg-muted/30', className)}>
      {!hasApp && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-background">
          <div className="text-center text-muted-foreground">
            <p className="text-sm">No app generated yet</p>
            <p className="text-xs">Start a conversation to generate your app</p>
          </div>
        </div>
      )}
      <iframe key={refreshKey} src={previewUrl} className="h-full w-full border-0" title="App Preview" />
    </div>
  )
})

PreviewPane.displayName = 'PreviewPane'
