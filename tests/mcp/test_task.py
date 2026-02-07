"""Tests for task and project Pydantic models."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import ValidationError
import pytest


class TestTaskStatus:
    """Tests for the TaskStatus enum."""

    def test_status_pending(self) -> None:
        """TaskStatus must include pending."""
        from codeagent.mcp.models.task import TaskStatus

        assert TaskStatus.PENDING == "pending"

    def test_status_in_progress(self) -> None:
        """TaskStatus must include in_progress."""
        from codeagent.mcp.models.task import TaskStatus

        assert TaskStatus.IN_PROGRESS == "in_progress"

    def test_status_done(self) -> None:
        """TaskStatus must include done."""
        from codeagent.mcp.models.task import TaskStatus

        assert TaskStatus.DONE == "done"

    def test_status_blocked(self) -> None:
        """TaskStatus must include blocked."""
        from codeagent.mcp.models.task import TaskStatus

        assert TaskStatus.BLOCKED == "blocked"

    def test_status_is_str_enum(self) -> None:
        """TaskStatus values should be usable as strings."""
        from codeagent.mcp.models.task import TaskStatus

        assert isinstance(TaskStatus.PENDING, str)


class TestTaskType:
    """Tests for the TaskType enum."""

    def test_type_task(self) -> None:
        """TaskType must include task."""
        from codeagent.mcp.models.task import TaskType

        assert TaskType.TASK == "task"

    def test_type_epic(self) -> None:
        """TaskType must include epic."""
        from codeagent.mcp.models.task import TaskType

        assert TaskType.EPIC == "epic"

    def test_type_is_str_enum(self) -> None:
        """TaskType values should be usable as strings."""
        from codeagent.mcp.models.task import TaskType

        assert isinstance(TaskType.TASK, str)


class TestTask:
    """Tests for the Task model."""

    def test_create_task_with_required_fields(self) -> None:
        """Task should be constructable with required fields."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        task = Task(
            task_id="CA-TASK-001",
            project="project:abc",
            name="Implement auth",
            created_at=now,
            updated_at=now,
        )
        assert task.task_id == "CA-TASK-001"
        assert task.project == "project:abc"
        assert task.name == "Implement auth"

    def test_task_defaults(self) -> None:
        """Task should have sensible defaults."""
        from codeagent.mcp.models.task import Task, TaskStatus, TaskType

        now = datetime.now(tz=UTC)
        task = Task(
            task_id="CA-TASK-001",
            project="project:abc",
            name="Test task",
            created_at=now,
            updated_at=now,
        )
        assert task.type == TaskType.TASK
        assert task.status == TaskStatus.PENDING
        assert task.priority == 3
        assert task.description is None
        assert task.files_exclusive == []
        assert task.files_readonly == []
        assert task.depends_on == []
        assert task.parent is None
        assert task.resolved_by is None
        assert task.suggested_model is None

    def test_task_with_all_fields(self) -> None:
        """Task should accept all optional fields."""
        from codeagent.mcp.models.task import Task, TaskStatus, TaskType

        now = datetime.now(tz=UTC)
        task = Task(
            task_id="CA-TASK-002",
            project="project:abc",
            name="Complex task",
            type=TaskType.EPIC,
            description="A big epic",
            status=TaskStatus.IN_PROGRESS,
            priority=1,
            files_exclusive=["src/auth.py"],
            files_readonly=["src/config.py"],
            depends_on=["task:xyz"],
            parent="task:parent1",
            resolved_by="memory:solution1",
            suggested_model="opus",
            created_at=now,
            updated_at=now,
        )
        assert task.type == TaskType.EPIC
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == 1
        assert task.files_exclusive == ["src/auth.py"]
        assert task.depends_on == ["task:xyz"]
        assert task.suggested_model == "opus"

    def test_task_rejects_invalid_status(self) -> None:
        """Task should reject an invalid status value."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            Task(
                task_id="CA-TASK-001",
                project="project:abc",
                name="Bad status",
                status="invalid",  # type: ignore[arg-type]
                created_at=now,
                updated_at=now,
            )

    def test_task_rejects_invalid_type(self) -> None:
        """Task should reject an invalid type value."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            Task(
                task_id="CA-TASK-001",
                project="project:abc",
                name="Bad type",
                type="story",  # type: ignore[arg-type]
                created_at=now,
                updated_at=now,
            )

    def test_task_priority_validation_low_bound(self) -> None:
        """Task priority must be >= 1."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            Task(
                task_id="CA-TASK-001",
                project="project:abc",
                name="Bad priority",
                priority=0,
                created_at=now,
                updated_at=now,
            )

    def test_task_priority_validation_high_bound(self) -> None:
        """Task priority must be <= 5."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            Task(
                task_id="CA-TASK-001",
                project="project:abc",
                name="Bad priority",
                priority=6,
                created_at=now,
                updated_at=now,
            )

    def test_task_serializes_to_dict(self) -> None:
        """Task should serialize to a dict cleanly."""
        from codeagent.mcp.models.task import Task

        now = datetime.now(tz=UTC)
        task = Task(
            task_id="CA-TASK-001",
            project="project:abc",
            name="Serialize test",
            created_at=now,
            updated_at=now,
        )
        data = task.model_dump()
        assert data["task_id"] == "CA-TASK-001"
        assert data["status"] == "pending"
        assert data["type"] == "task"
        assert data["priority"] == 3


class TestTaskCreate:
    """Tests for the TaskCreate input model."""

    def test_create_with_required_fields(self) -> None:
        """TaskCreate should work with required fields."""
        from codeagent.mcp.models.task import TaskCreate

        create = TaskCreate(
            task_id="CA-TASK-001",
            project="project:abc",
            name="New task",
        )
        assert create.task_id == "CA-TASK-001"
        assert create.project == "project:abc"
        assert create.name == "New task"

    def test_create_defaults(self) -> None:
        """TaskCreate should have sensible defaults."""
        from codeagent.mcp.models.task import TaskCreate, TaskStatus, TaskType

        create = TaskCreate(
            task_id="CA-TASK-001",
            project="project:abc",
            name="New task",
        )
        assert create.type == TaskType.TASK
        assert create.status == TaskStatus.PENDING
        assert create.priority == 3
        assert create.description is None
        assert create.files_exclusive == []
        assert create.files_readonly == []
        assert create.depends_on == []
        assert create.parent is None
        assert create.suggested_model is None

    def test_create_with_all_fields(self) -> None:
        """TaskCreate should accept all optional fields."""
        from codeagent.mcp.models.task import TaskCreate, TaskStatus, TaskType

        create = TaskCreate(
            task_id="CA-TASK-002",
            project="project:abc",
            name="Full task",
            type=TaskType.EPIC,
            description="An epic task",
            status=TaskStatus.BLOCKED,
            priority=5,
            files_exclusive=["src/main.py"],
            files_readonly=["src/config.py"],
            depends_on=["task:dep1"],
            parent="task:parent1",
            suggested_model="haiku",
        )
        assert create.type == TaskType.EPIC
        assert create.priority == 5

    def test_create_requires_task_id(self) -> None:
        """TaskCreate should require task_id."""
        from codeagent.mcp.models.task import TaskCreate

        with pytest.raises(ValidationError):
            TaskCreate(project="project:abc", name="Missing ID")  # type: ignore[call-arg]

    def test_create_requires_project(self) -> None:
        """TaskCreate should require project."""
        from codeagent.mcp.models.task import TaskCreate

        with pytest.raises(ValidationError):
            TaskCreate(task_id="CA-TASK-001", name="Missing project")  # type: ignore[call-arg]

    def test_create_requires_name(self) -> None:
        """TaskCreate should require name."""
        from codeagent.mcp.models.task import TaskCreate

        with pytest.raises(ValidationError):
            TaskCreate(task_id="CA-TASK-001", project="project:abc")  # type: ignore[call-arg]


class TestProject:
    """Tests for the Project model."""

    def test_create_project_with_required_fields(self) -> None:
        """Project should be constructable with name and prefix."""
        from codeagent.mcp.models.task import Project

        proj = Project(name="CodeAgent", prefix="CA")
        assert proj.name == "CodeAgent"
        assert proj.prefix == "CA"

    def test_project_description_optional(self) -> None:
        """Project.description should default to None."""
        from codeagent.mcp.models.task import Project

        proj = Project(name="Test", prefix="TST")
        assert proj.description is None

    def test_project_with_description(self) -> None:
        """Project should accept an optional description."""
        from codeagent.mcp.models.task import Project

        proj = Project(
            name="CodeAgent",
            prefix="CA",
            description="AI coding framework",
        )
        assert proj.description == "AI coding framework"

    def test_project_created_at_optional(self) -> None:
        """Project.created_at should default to None when not provided."""
        from codeagent.mcp.models.task import Project

        proj = Project(name="Test", prefix="TST")
        assert proj.created_at is None

    def test_project_with_created_at(self) -> None:
        """Project should accept created_at timestamp."""
        from codeagent.mcp.models.task import Project

        now = datetime.now(tz=UTC)
        proj = Project(name="Test", prefix="TST", created_at=now)
        assert proj.created_at == now

    def test_project_requires_name(self) -> None:
        """Project should require name."""
        from codeagent.mcp.models.task import Project

        with pytest.raises(ValidationError):
            Project(prefix="CA")  # type: ignore[call-arg]

    def test_project_requires_prefix(self) -> None:
        """Project should require prefix."""
        from codeagent.mcp.models.task import Project

        with pytest.raises(ValidationError):
            Project(name="CodeAgent")  # type: ignore[call-arg]

    def test_project_serializes_to_dict(self) -> None:
        """Project should serialize cleanly."""
        from codeagent.mcp.models.task import Project

        proj = Project(name="CodeAgent", prefix="CA", description="Framework")
        data = proj.model_dump()
        assert data["name"] == "CodeAgent"
        assert data["prefix"] == "CA"
        assert data["description"] == "Framework"
