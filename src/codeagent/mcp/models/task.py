"""Pydantic models for the task and project domains.

Covers project organization, task tracking with priority/status,
file boundaries for parallel execution, and dependency management.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    """Valid statuses for a task record.

    Lifecycle: pending -> in_progress -> done
    Can also be: blocked (waiting on dependency)
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskType(StrEnum):
    """Discriminator for task granularity.

    An epic contains multiple child tasks.
    """

    TASK = "task"
    EPIC = "epic"


class Task(BaseModel):
    """Full task record as stored in SurrealDB.

    Attributes:
        task_id: Human-readable task identifier (e.g. "CA-TASK-001").
        project: SurrealDB record ID of the parent project.
        name: Short name describing the task.
        type: Whether this is a task or an epic.
        description: Optional longer description.
        status: Current task status.
        priority: Priority 1 (highest) to 5 (lowest).
        files_exclusive: Files only this task may modify.
        files_readonly: Files this task may read but not modify.
        depends_on: List of task record IDs this task depends on.
        parent: Optional parent task (for sub-tasks of epics).
        resolved_by: Optional memory record ID that resolved this task.
        suggested_model: Optional model suggestion (e.g. "haiku", "opus").
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    task_id: str
    project: str
    name: str
    type: TaskType = TaskType.TASK
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=3, ge=1, le=5)
    files_exclusive: list[str] = Field(default_factory=list)
    files_readonly: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    parent: str | None = None
    resolved_by: str | None = None
    suggested_model: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    """Input model for creating a new task.

    Requires task_id, project, and name. All other fields have defaults.

    Attributes:
        task_id: Human-readable task identifier.
        project: SurrealDB record ID of the parent project.
        name: Short name describing the task.
        type: Whether this is a task or an epic.
        description: Optional longer description.
        status: Initial task status.
        priority: Priority 1 (highest) to 5 (lowest).
        files_exclusive: Files only this task may modify.
        files_readonly: Files this task may read but not modify.
        depends_on: List of task record IDs this task depends on.
        parent: Optional parent task record ID.
        suggested_model: Optional model suggestion.
    """

    task_id: str
    project: str
    name: str
    type: TaskType = TaskType.TASK
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=3, ge=1, le=5)
    files_exclusive: list[str] = Field(default_factory=list)
    files_readonly: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    parent: str | None = None
    suggested_model: str | None = None


class Project(BaseModel):
    """Project record for organizing tasks and memories.

    Attributes:
        name: Human-readable project name.
        prefix: Short prefix for task IDs (e.g. "CA").
        description: Optional project description.
        created_at: Timestamp of creation. None before persistence.
    """

    name: str
    prefix: str
    description: str | None = None
    created_at: datetime | None = None
