"""FastAPI server for the React builder agent."""

import logfire
from fastapi import FastAPI

from .agent import run_agent
from .models import CreateAppRequest, CreateAppResponse, EditAppRequest, EditAppResponse

logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI(
    title='React Builder Agent',
    description='A pydantic-ai powered agent that builds React applications',
)
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
