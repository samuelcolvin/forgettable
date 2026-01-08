import type { ChatStatus, UIMessage } from 'ai'

import { CodeBlock } from '@/components/ai-elements/code-block'
import { Message, MessageContent } from '@/components/ai-elements/message'
import { Response } from '@/components/ai-elements/response'
import { Tool, ToolContent, ToolHeader, ToolInput, ToolOutput } from '@/components/ai-elements/tool'

interface PartProps {
  part: UIMessage['parts'][number]
  message: UIMessage
  status: ChatStatus
}

export function Part({ part, message }: PartProps) {
  if (part.type === 'text') {
    return (
      <div className="py-2">
        <Message from={message.role}>
          <MessageContent>
            <Response>{part.text}</Response>
          </MessageContent>
        </Message>
      </div>
    )
  }

  // Handle tool parts - they have type like 'tool-create_file'
  if (part.type.startsWith('tool-') && 'toolCallId' in part) {
    const toolName = part.type.slice(5) // Remove 'tool-' prefix
    return (
      <div className="py-2">
        <Tool defaultOpen={part.state !== 'output-available'}>
          <ToolHeader toolName={toolName} state={part.state} />
          <ToolContent>
            <ToolInput input={part.input} />
            {part.state === 'output-available' && (
              <ToolOutput
                error={undefined}
                output={
                  typeof part.output === 'string' ? (
                    part.output
                  ) : (
                    <CodeBlock code={JSON.stringify(part.output, null, 2)} language="json" />
                  )
                }
              />
            )}
            {part.state === 'output-error' && 'errorText' in part && (
              <ToolOutput error={part.errorText} output={null} />
            )}
          </ToolContent>
        </Tool>
      </div>
    )
  }

  // Handle other part types if needed
  return null
}
