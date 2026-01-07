"""React builder agent using pydantic-ai."""

from pydantic_ai import Agent, RunContext

from .models import AgentOutput, AppDependencies, Diff, DiffHunk

SYSTEM_INSTRUCTIONS = """You are a React application builder. Create client-side React applications following these rules:

1. All code must be TypeScript (.tsx or .ts files)
2. Only React and TailwindCSS are available as dependencies
3. Every function and class must have a docstring
4. Non-trivial logic must have concise explanation comments
5. Use modern React patterns (hooks, functional components)
6. Structure: src/App.tsx as entry, components in src/components/

When creating files, use appropriate file paths like:
- src/App.tsx for the main app component
- src/components/ComponentName.tsx for components
- src/types.ts for TypeScript type definitions
- src/hooks/useHookName.ts for custom hooks

Always provide a summary of what you built and list your design decisions."""

agent: Agent[AppDependencies, AgentOutput] = Agent(
    'gateway/anthropic:claude-opus-4-5',
    deps_type=AppDependencies,
    output_type=AgentOutput,
    instructions=SYSTEM_INSTRUCTIONS,
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
) -> tuple[dict[str, str], dict[str, Diff], AgentOutput]:
    """Run the React builder agent.

    Args:
        prompt: The user's prompt describing what to build or modify.
        existing_files: Optional dict of existing files when editing an app.

    Returns:
        A tuple of (files, diffs, output) where:
        - files: The final state of all files
        - diffs: Any diffs that were applied (for edit operations)
        - output: The agent's structured output with summary and design decisions
    """
    deps = AppDependencies(files=existing_files.copy() if existing_files else {})
    result = await agent.run(prompt, deps=deps)
    return deps.files, deps.diffs, result.output
