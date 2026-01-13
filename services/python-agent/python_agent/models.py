"""Shared Pydantic models and dataclasses for the React builder agent."""

from dataclasses import dataclass, field

from pydantic import BaseModel


class CreateAppRequest(BaseModel):
    """Request to create a new React app."""

    prompt: str


class CreateAppResponse(BaseModel):
    """Response containing generated files and summary."""

    files: dict[str, str]
    compiled_files: dict[str, str]
    summary: str


class EditAppRequest(BaseModel):
    """Request to edit an existing app."""

    prompt: str
    files: dict[str, str]


class EditAppResponse(BaseModel):
    """Response containing edited files."""

    files: dict[str, str]
    compiled_files: dict[str, str]
    summary: str


@dataclass
class AppDependencies:
    """Mutable state passed to agent tools."""

    files: dict[str, str] = field(default_factory=dict)
    compiled_files: dict[str, str] = field(default_factory=dict)
