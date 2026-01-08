import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport, type UIMessage } from 'ai'
import { type FormEvent, useEffect, useMemo, useRef, useState } from 'react'

import { Conversation, ConversationContent, ConversationScrollButton } from '@/components/ai-elements/conversation'
import { Loader } from '@/components/ai-elements/loader'
import {
  PromptInput,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputToolbar,
} from '@/components/ai-elements/prompt-input'

import { Part } from './Part'

const FILE_OP_TOOLS = new Set(['create_file', 'edit_file', 'delete_file'])

interface ChatProps {
  projectId: string
  onFileChange?: () => void
}

function hasCompletedFileOp(message: UIMessage): boolean {
  for (const part of message.parts) {
    // Tool parts have type like 'tool-create_file'
    if (part.type.startsWith('tool-') && 'state' in part && part.state === 'output-available') {
      const toolName = part.type.slice(5) // Remove 'tool-' prefix
      if (FILE_OP_TOOLS.has(toolName)) {
        return true
      }
    }
  }
  return false
}

export function Chat({ projectId, onFileChange }: ChatProps) {
  const [input, setInput] = useState('')
  const transport = useMemo(() => new DefaultChatTransport({ api: `/api/${projectId}/chat` }), [projectId])
  const { messages, sendMessage, status, error } = useChat({ transport })
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lastRefreshedMsgRef = useRef<string>('')

  // Detect completed file operations and trigger refresh
  useEffect(() => {
    const lastMsg = messages.at(-1)
    if (!lastMsg || lastMsg.role !== 'assistant') return

    if (hasCompletedFileOp(lastMsg) && lastRefreshedMsgRef.current !== lastMsg.id) {
      lastRefreshedMsgRef.current = lastMsg.id
      onFileChange?.()
    }
  }, [messages, onFileChange])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      sendMessage({ text: input }).catch((err: unknown) => {
        console.error('Error sending message:', err)
      })
      setInput('')
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-4 py-3">
        <h2 className="font-semibold text-lg">Forgettable</h2>
        <p className="text-muted-foreground text-xs">
          You are limited only by the paucity of your own imagination ... go on, build it
        </p>
      </div>

      <Conversation className="flex-1">
        <ConversationContent>
          {messages.map((message) => (
            <div key={message.id}>
              {message.parts.map((part, i) => (
                <Part key={`${message.id}-${i}`} part={part} message={message} status={status} />
              ))}
            </div>
          ))}
          {status === 'submitted' && <Loader />}
          {status === 'error' && error && (
            <div className="mx-4 my-2 rounded-md border border-destructive/20 bg-destructive/10 px-4 py-3 text-destructive text-sm">
              <strong>Error:</strong> {error.message}
            </div>
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      <div className="sticky bottom-0 border-t bg-background p-3">
        <PromptInput onSubmit={handleSubmit}>
          <PromptInputTextarea ref={textareaRef} onChange={(e) => setInput(e.target.value)} value={input} autoFocus />
          <PromptInputToolbar>
            <PromptInputSubmit disabled={!input.trim()} status={status} />
          </PromptInputToolbar>
        </PromptInput>
      </div>
    </div>
  )
}
