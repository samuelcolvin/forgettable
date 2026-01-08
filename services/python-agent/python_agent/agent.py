"""React builder agent using pydantic-ai."""

import os

import httpx
import logfire
from pydantic_ai import Agent, ModelRetry, RunContext, TextOutput

from .models import AppDependencies, Diff, DiffHunk

BUILD_ENDPOINT = os.environ.get('BUILD_ENDPOINT', 'http://localhost:3000/build')

# MODEL = 'gateway/anthropic:claude-opus-4-5'
# MODEL = 'gateway/anthropic:claude-sonnet-4-5'
MODEL = 'gateway/anthropic:claude-haiku-4-5'

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

Always provide a summary of what you built and list your design decisions."""


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
            ctx.deps.compiled_files = response.json()
            return text
        raise ModelRetry(response.text)


agent: Agent[AppDependencies, str] = Agent(
    MODEL,
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
def edit_file(ctx: RunContext[AppDependencies], file_path: str, diff: Diff) -> str:
    """Edit an existing file by applying search/replace operations.

    Args:
        ctx: The run context containing app dependencies.
        file_path: The path of the file to edit.
        diff: A Diff object containing hunks of search/replace operations.

    Returns:
        A confirmation message indicating the changes made.
    """
    if file_path not in ctx.deps.files:
        return f'Error: File {file_path} does not exist'

    content = ctx.deps.files[file_path]
    changes_made: list[str] = []

    for hunk in diff.hunks:
        if hunk.search in content:
            content = content.replace(hunk.search, hunk.replace, 1)
            changes_made.append(f'Replaced "{hunk.search[:30]}..." with "{hunk.replace[:30]}..."')
        else:
            changes_made.append(f'Warning: Could not find "{hunk.search[:30]}..." in file')

    ctx.deps.files[file_path] = content

    # Track the diff for this file
    if file_path in ctx.deps.diffs:
        ctx.deps.diffs[file_path].hunks.extend(diff.hunks)
    else:
        ctx.deps.diffs[file_path] = diff

    return f'Edited file: {file_path}. Changes: {"; ".join(changes_made)}'


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

    # Track the deletion as a special diff
    ctx.deps.diffs[file_path] = Diff(hunks=[DiffHunk(search='<entire file>', replace='<deleted>')])

    return f'Deleted file: {file_path}'


async def run_agent(
    prompt: str,
    existing_files: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, str], dict[str, Diff], str]:
    """Run the React builder agent.

    Args:
        prompt: The user's prompt describing what to build or modify.
        existing_files: Optional dict of existing files when editing an app.

    Returns:
        A tuple of (files, compiled_files, diffs, summary) where:
        - files: The final state of all source files
        - compiled_files: The compiled js/css/sourcemap files from the build
        - diffs: Any diffs that were applied (for edit operations)
        - summary: The summary string from the model
    """
    deps = AppDependencies(files=existing_files.copy() if existing_files else {})
    result = await agent.run(prompt, deps=deps)
    return deps.files, deps.compiled_files, deps.diffs, result.output
