"""React builder agent using pydantic-ai."""

import os

import httpx
import logfire
from pydantic_ai import Agent, ModelRetry, RunContext, TextOutput
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.gateway import gateway_provider

from .models import AppDependencies

BUILD_ENDPOINT = os.environ.get('BUILD_ENDPOINT', 'http://localhost:3002/build')

SYSTEM_INSTRUCTIONS = """\
You are a React application builder. Create client-side React applications following these rules:

1. All code must be TypeScript (.tsx or .ts files)
2. React, TailwindCSS, and shadcn/ui components are available
3. Every function and class must have a docstring
4. Non-trivial logic must have concise explanation comments
5. Use modern React patterns (hooks, functional components)
6. Structure: app.tsx as entry point, components in components/
7. Use shadcn/ui components for professional, accessible UI:
   - Import from "shadcn/components/ui/[component]"
   - Available: Button, Card, Input, Label, Badge, Alert, Separator, Progress, Checkbox, Switch, Tabs,
     Tooltip, Dialog, Select, ScrollArea, AlertDialog, DropdownMenu, Avatar, Accordion, Popover, Table
   - Use lucide-react for icons: import { Icon } from "lucide-react"
   - Example: import { Button } from "shadcn/components/ui/button"

When creating files, use appropriate file paths like:
- app.tsx for the main app component (required, default export)
- components/ComponentName.tsx for components
- types.ts for TypeScript type definitions
- hooks/useHookName.ts for custom hooks

Always provide a brief summary of what you built, and anything important to watch out for.
Keep this summary concise and to the point, avoid use of emojis.
"""


async def submit_files(ctx: RunContext[AppDependencies], text: str) -> str:
    """Submit the generated files to the build endpoint.

    Args:
        ctx: The run context containing app dependencies with files.
        text: The summary text from the model.

    Returns:
        The summary text. Compiled files are stored in ctx.deps.compiled_files.

    Raises:
        ModelRetry: If the build endpoint returns a non-200 status, allowing the model to retry.
    """
    if os.environ.get('SKIP_VALIDATION'):
        return text

    async with httpx.AsyncClient() as client:
        logfire.instrument_httpx(client)
        response = await client.post(
            BUILD_ENDPOINT,
            json={'files': ctx.deps.files},
            timeout=60.0,
        )
        if response.status_code == 200:
            data = response.json()
            ctx.deps.compiled_files = data['compiled']
            # Update source files with biome's auto-fixes
            ctx.deps.files.update(data['source'])
            return text
        raise ModelRetry(response.text)


# model = 'gateway/anthropic:claude-opus-4-5'
# model = 'gateway/anthropic:claude-sonnet-4-5'
# model = 'gateway/anthropic:claude-haiku-4-5'
provider = gateway_provider('anthropic', route='builtin-google-vertex')
model = AnthropicModel('claude-sonnet-4-5', provider=provider)
agent: Agent[AppDependencies, str] = Agent(
    model,
    deps_type=AppDependencies,
    output_type=TextOutput(submit_files),
    instructions=SYSTEM_INSTRUCTIONS,
    retries=10,
)


@agent.tool
def create_file(ctx: RunContext[AppDependencies], file_path: str, content: str) -> str:
    """Create a new file with the given content.

    Args:
        ctx: The run context containing app dependencies.
        file_path: The path where the file should be created (e.g., 'src/App.tsx').
        content: The content to write to the file.

    Returns:
        A confirmation message indicating the file was created.
    """
    ctx.deps.files[file_path] = content
    return f'Created file: {file_path}'


@agent.tool
def edit_file(
    ctx: RunContext[AppDependencies],
    path: str,
    old_str: str,
    new_str: str,
    replace_all: bool = False,
) -> str:
    """Edit a file by replacing a specific string with another string.

    Args:
        ctx: The run context containing app dependencies.
        path: The file path.
        old_str: The exact text to find (must match uniquely).
        new_str: The replacement text.
        replace_all: Whether to replace all occurrences. Defaults to False.

    Returns:
        Summary of the changes made.
    """
    if path not in ctx.deps.files:
        return f'Error: File {path} does not exist'

    content = ctx.deps.files[path]

    if old_str not in content:
        return f'Error: Could not find "{old_str[:50]}..." in {path}'

    if replace_all:
        count = content.count(old_str)
        content = content.replace(old_str, new_str)
        summary = f'Replaced {count} occurrence(s)'
    else:
        content = content.replace(old_str, new_str, 1)
        summary = 'Replaced 1 occurrence'

    ctx.deps.files[path] = content
    return f'Edited {path}: {summary}'


@agent.tool
def delete_file(ctx: RunContext[AppDependencies], file_path: str) -> str:
    """Delete a file.

    Args:
        ctx: The run context containing app dependencies.
        file_path: The path of the file to delete.

    Returns:
        A confirmation message indicating the file was deleted.
    """
    if file_path not in ctx.deps.files:
        return f'Error: File {file_path} does not exist'

    del ctx.deps.files[file_path]
    return f'Deleted file: {file_path}'


async def run_agent(
    prompt: str,
    existing_files: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, str], str]:
    """Run the React builder agent.

    Args:
        prompt: The user's prompt describing what to build or modify.
        existing_files: Optional dict of existing files when editing an app.

    Returns:
        A tuple of (files, compiled_files, summary) where:
        - files: The final state of all source files
        - compiled_files: The compiled js/css/sourcemap files from the build
        - summary: The summary string from the model
    """
    deps = AppDependencies(files=existing_files.copy() if existing_files else {})
    result = await agent.run(prompt, deps=deps)
    return deps.files, deps.compiled_files, result.output
