import { FileEditIcon, FilePlusIcon, FileXIcon, WrenchIcon } from 'lucide-react'
import type { ReactNode } from 'react'

export function getToolIcon(toolId: string, className = 'size-4'): ReactNode {
  const iconMap: Record<string, ReactNode> = {
    create_file: <FilePlusIcon className={className} />,
    edit_file: <FileEditIcon className={className} />,
    delete_file: <FileXIcon className={className} />,
  }
  return iconMap[toolId] ?? <WrenchIcon className={className} />
}
