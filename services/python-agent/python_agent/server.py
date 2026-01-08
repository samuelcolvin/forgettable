"""FastAPI server for the React builder agent."""

import os

import logfire
from fastapi import FastAPI
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from starlette.requests import Request
from starlette.responses import Response

from .agent import agent, run_agent
from .models import AppDependencies, CreateAppRequest, CreateAppResponse, EditAppRequest, EditAppResponse

if os.environ.get('LOGFIRE_TOKEN'):
    logfire.configure(service_name='agent', distributed_tracing=True)
    logfire.instrument_pydantic_ai()

app = FastAPI(
    title='React Builder Agent',
    description='A pydantic-ai powered agent that builds React applications',
)
if os.environ.get('LOGFIRE_TOKEN'):
    logfire.instrument_fastapi(app)


@app.post('/apps')
async def create_app(request: CreateAppRequest) -> CreateAppResponse:
    """Create a new React application based on the given prompt.

    Args:
        request: The request containing the prompt for the app to build.

    Returns:
        The generated files and a summary of the application.
    """
    files, compiled_files, _, summary = await run_agent(request.prompt)
    return CreateAppResponse(files=files, compiled_files=compiled_files, summary=summary)


@app.post('/apps/edit')
async def edit_app(request: EditAppRequest) -> EditAppResponse:
    """Edit an existing React application based on the given prompt.

    Args:
        request: The request containing the prompt and existing files.

    Returns:
        The diffs applied, final files, and a summary of the changes.
    """
    files, compiled_files, diffs, summary = await run_agent(request.prompt, request.files)
    return EditAppResponse(diffs=diffs, files=files, compiled_files=compiled_files, summary=summary)


@app.post('/chat')
async def chat(request: Request) -> Response:
    """Handle streaming chat via Vercel AI SDK protocol.

    This endpoint implements the Vercel AI SDK protocol for real-time streaming
    chat with the React builder agent. Tool calls (create_file, edit_file, delete_file)
    are streamed to the client as they occur.

    Args:
        request: The Starlette request containing the chat message.

    Returns:
        A streaming response with Server-Sent Events containing the agent's response.
    """
    # Parse the request body to extract any existing files
    body = await request.json()
    files = body.get('files', {})

    # Create dependencies with existing files
    deps = AppDependencies(files=files)

    return await VercelAIAdapter.dispatch_request(request, agent=agent, deps=deps)
