"""Tests for SurrealDB client."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from codeagent.mcp.db.client import SurrealDBClient


@pytest.fixture()
def mock_surreal() -> MagicMock:
    """Create a mock Surreal client."""
    mock = MagicMock()
    mock.connect = AsyncMock()
    mock.close = AsyncMock()
    mock.signin = AsyncMock()
    mock.use = AsyncMock()
    mock.query = AsyncMock()
    mock.create = AsyncMock()
    mock.select = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture()
def _patch_surreal(mock_surreal: MagicMock) -> Generator[MagicMock]:
    """Patch AsyncSurreal to return our mock."""
    with patch("codeagent.mcp.db.client.AsyncSurreal", return_value=mock_surreal):
        yield mock_surreal


@pytest_asyncio.fixture()
async def client(_patch_surreal: MagicMock) -> SurrealDBClient:
    """Create a connected SurrealDBClient with mocked backend."""
    from codeagent.mcp.db.client import SurrealDBClient

    db_client = SurrealDBClient()
    await db_client.connect()
    return db_client


class TestSurrealDBClientConnection:
    """Tests for connection lifecycle."""

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_connect_establishes_connection(
        self, mock_surreal: MagicMock
    ) -> None:
        """Test that connect() establishes a connection to SurrealDB."""
        from codeagent.mcp.db.client import SurrealDBClient

        client = SurrealDBClient()
        await client.connect()

        mock_surreal.connect.assert_called_once()
        mock_surreal.signin.assert_called_once()
        mock_surreal.use.assert_called_once()

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_connect_uses_custom_url(self, mock_surreal: MagicMock) -> None:
        """Test that connect() uses custom URL when provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        client = SurrealDBClient(url="ws://custom:8080")
        await client.connect()

        mock_surreal.connect.assert_called_once_with("ws://custom:8080")

    @pytest.mark.asyncio()
    async def test_close_closes_connection(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that close() properly closes the connection."""
        await client.close()

        mock_surreal.close.assert_called_once()

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_context_manager_connects_and_closes(
        self, mock_surreal: MagicMock
    ) -> None:
        """Test async context manager manages connection lifecycle."""
        from codeagent.mcp.db.client import SurrealDBClient

        async with SurrealDBClient() as ctx_client:
            assert ctx_client is not None
            mock_surreal.connect.assert_called_once()

        mock_surreal.close.assert_called_once()

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_connect_closes_on_signin_failure(
        self, mock_surreal: MagicMock
    ) -> None:
        """Test that connect() closes connection if signin fails."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.signin = AsyncMock(side_effect=Exception("Auth failed"))

        client = SurrealDBClient()
        with pytest.raises(Exception, match="Auth failed"):
            await client.connect()

        mock_surreal.connect.assert_called_once()
        mock_surreal.close.assert_called_once()

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_connect_closes_on_use_failure(self, mock_surreal: MagicMock) -> None:
        """Test that connect() closes connection if namespace selection fails."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.use = AsyncMock(side_effect=Exception("NS not found"))

        client = SurrealDBClient()
        with pytest.raises(Exception, match="NS not found"):
            await client.connect()

        mock_surreal.connect.assert_called_once()
        mock_surreal.signin.assert_called_once()
        mock_surreal.close.assert_called_once()


class TestSurrealDBClientConfig:
    """Tests for client configuration."""

    @pytest.mark.asyncio()
    async def test_default_credentials(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that default credentials are used for signin."""
        mock_surreal.signin.assert_called_once_with(
            {"username": "root", "password": "root"}
        )

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_custom_credentials(self, mock_surreal: MagicMock) -> None:
        """Test that custom credentials can be provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        client = SurrealDBClient(
            username="admin",
            password="secret",  # noqa: S106
        )
        await client.connect()

        mock_surreal.signin.assert_called_once_with(
            {"username": "admin", "password": "secret"}
        )

    @pytest.mark.asyncio()
    async def test_default_namespace_and_database(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that default namespace and database are used."""
        mock_surreal.use.assert_called_once_with("codeagent", "codeagent")

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_patch_surreal")
    async def test_custom_namespace_and_database(self, mock_surreal: MagicMock) -> None:
        """Test that custom namespace and database can be provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        client = SurrealDBClient(namespace="custom_ns", database="custom_db")
        await client.connect()

        mock_surreal.use.assert_called_once_with("custom_ns", "custom_db")


class TestSurrealDBClientOperations:
    """Tests for CRUD and query operations."""

    @pytest.mark.asyncio()
    async def test_create_delegates_to_surreal(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that create() delegates to the underlying client."""
        mock_surreal.create = AsyncMock(return_value=[{"id": "test:1", "name": "test"}])

        result = await client.create("test", {"name": "test"})

        mock_surreal.create.assert_called_once_with("test", {"name": "test"})
        assert result == [{"id": "test:1", "name": "test"}]

    @pytest.mark.asyncio()
    async def test_select_delegates_to_surreal(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that select() delegates to the underlying client."""
        mock_surreal.select = AsyncMock(return_value=[{"id": "test:1"}])

        result = await client.select("test")

        mock_surreal.select.assert_called_once_with("test")
        assert result == [{"id": "test:1"}]

    @pytest.mark.asyncio()
    async def test_update_delegates_to_surreal(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that update() delegates to the underlying client."""
        mock_surreal.update = AsyncMock(
            return_value=[{"id": "test:1", "name": "updated"}]
        )

        result = await client.update("test:1", {"name": "updated"})

        mock_surreal.update.assert_called_once_with("test:1", {"name": "updated"})
        assert result == [{"id": "test:1", "name": "updated"}]

    @pytest.mark.asyncio()
    async def test_delete_delegates_to_surreal(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that delete() delegates to the underlying client."""
        mock_surreal.delete = AsyncMock(return_value=[{"id": "test:1"}])

        result = await client.delete("test:1")

        mock_surreal.delete.assert_called_once_with("test:1")
        assert result == [{"id": "test:1"}]

    @pytest.mark.asyncio()
    async def test_query_delegates_to_surreal(
        self, client: SurrealDBClient, mock_surreal: MagicMock
    ) -> None:
        """Test that query() delegates raw SurQL to the underlying client."""
        mock_surreal.query = AsyncMock(return_value=[{"result": [{"id": "test:1"}]}])

        result = await client.query(
            "SELECT * FROM test WHERE id = $id",
            {"id": "test:1"},
        )

        mock_surreal.query.assert_called_once_with(
            "SELECT * FROM test WHERE id = $id", {"id": "test:1"}
        )
        assert result == [{"result": [{"id": "test:1"}]}]

    @pytest.mark.asyncio()
    async def test_initialize_schema_runs_schema_file(
        self, client: SurrealDBClient, mock_surreal: MagicMock, tmp_path: Path
    ) -> None:
        """Test that initialize_schema() loads and executes schema file."""
        schema_content = "DEFINE TABLE test SCHEMAFULL;"
        schema_file = tmp_path / "schema.surql"
        schema_file.write_text(schema_content)

        mock_surreal.query = AsyncMock(return_value=[{}])

        result = await client.initialize_schema(schema_file)

        mock_surreal.query.assert_called_once_with(schema_content)
        assert result == [{}]
