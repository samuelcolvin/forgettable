"""FastAPI server for the React builder agent."""

from fastapi import FastAPI

from .agent import run_agent
from .models import CreateAppRequest, CreateAppResponse, EditAppRequest, EditAppResponse

app = FastAPI(
    title='React Builder Agent',
    description='A pydantic-ai powered agent that builds React applications',
    version='0.1.0',
)


@app.post('/apps')
async def create_app(request: CreateAppRequest) -> CreateAppResponse:
    """Create a new React application based on the given prompt.

    Args:
        request: The request containing the prompt for the app to build.

    Returns:
        The generated files and a summary of the application.
    """
    files, _, summary = await run_agent(request.prompt)
    return CreateAppResponse(files=files, summary=summary)


@app.post('/apps/edit')
async def edit_app(request: EditAppRequest) -> EditAppResponse:
    """Edit an existing React application based on the given prompt.

    Args:
        request: The request containing the prompt and existing files.

    Returns:
        The diffs applied, final files, and a summary of the changes.
    """
    files, diffs, summary = await run_agent(request.prompt, request.files)
    return EditAppResponse(diffs=diffs, files=files, summary=summary)
