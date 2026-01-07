"""Shared Pydantic models and dataclasses for the React builder agent."""

from dataclasses import dataclass, field

from pydantic import BaseModel


class DiffHunk(BaseModel):
    """A single search/replace operation."""

    search: str
    replace: str


class Diff(BaseModel):
    """Collection of changes to apply to a file."""

    hunks: list[DiffHunk]


class CreateAppRequest(BaseModel):
    """Request to create a new React app."""

    prompt: str


class CreateAppResponse(BaseModel):
    """Response containing generated files and summary."""

    files: dict[str, str]
    summary: str


class EditAppRequest(BaseModel):
    """Request to edit an existing app."""

    prompt: str
    files: dict[str, str]


class EditAppResponse(BaseModel):
    """Response containing diffs applied to files."""

    diffs: dict[str, Diff]
    files: dict[str, str]
    summary: str


class AgentOutput(BaseModel):
    """Structured output from the agent."""

    summary: str
    design_decisions: list[str]


@dataclass
class AppDependencies:
    """Mutable state passed to agent tools."""

    files: dict[str, str] = field(default_factory=dict)
    diffs: dict[str, Diff] = field(default_factory=dict)
