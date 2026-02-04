"""Tests for SurrealDB client."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestSurrealDBClient:
    """Tests for the SurrealDB client wrapper."""

    @pytest.fixture
    def mock_surreal(self) -> MagicMock:
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

    @pytest.mark.asyncio
    async def test_connect_establishes_connection(self, mock_surreal: MagicMock) -> None:
        """Test that connect() establishes a connection to SurrealDB."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()

            mock_surreal.connect.assert_called_once()
            mock_surreal.signin.assert_called_once()
            mock_surreal.use.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_uses_custom_url(self, mock_surreal: MagicMock) -> None:
        """Test that connect() uses custom URL when provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient(url="ws://custom:8080")
            await client.connect()

            mock_surreal.connect.assert_called_once_with("ws://custom:8080")

    @pytest.mark.asyncio
    async def test_close_closes_connection(self, mock_surreal: MagicMock) -> None:
        """Test that close() properly closes the connection."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            await client.close()

            mock_surreal.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_connects_and_closes(
        self, mock_surreal: MagicMock
    ) -> None:
        """Test that async context manager properly manages connection lifecycle."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            async with SurrealDBClient() as client:
                assert client is not None
                mock_surreal.connect.assert_called_once()

            mock_surreal.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_schema_runs_schema_file(
        self, mock_surreal: MagicMock, tmp_path: Path
    ) -> None:
        """Test that initialize_schema() loads and executes schema file."""
        from codeagent.mcp.db.client import SurrealDBClient

        schema_content = "DEFINE TABLE test SCHEMAFULL;"
        schema_file = tmp_path / "schema.surql"
        schema_file.write_text(schema_content)

        mock_surreal.query = AsyncMock(return_value=[{}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            await client.initialize_schema(schema_file)

            mock_surreal.query.assert_called()

    @pytest.mark.asyncio
    async def test_create_inserts_record(self, mock_surreal: MagicMock) -> None:
        """Test that create() inserts a new record."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.create = AsyncMock(return_value=[{"id": "test:1", "name": "test"}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            result = await client.create("test", {"name": "test"})

            mock_surreal.create.assert_called_once_with("test", {"name": "test"})
            assert result == [{"id": "test:1", "name": "test"}]

    @pytest.mark.asyncio
    async def test_select_retrieves_records(self, mock_surreal: MagicMock) -> None:
        """Test that select() retrieves records by table or ID."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.select = AsyncMock(return_value=[{"id": "test:1"}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            result = await client.select("test")

            mock_surreal.select.assert_called_once_with("test")
            assert result == [{"id": "test:1"}]

    @pytest.mark.asyncio
    async def test_update_modifies_record(self, mock_surreal: MagicMock) -> None:
        """Test that update() modifies an existing record."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.update = AsyncMock(return_value=[{"id": "test:1", "name": "updated"}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            result = await client.update("test:1", {"name": "updated"})

            mock_surreal.update.assert_called_once_with("test:1", {"name": "updated"})
            assert result == [{"id": "test:1", "name": "updated"}]

    @pytest.mark.asyncio
    async def test_delete_removes_record(self, mock_surreal: MagicMock) -> None:
        """Test that delete() removes a record."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.delete = AsyncMock(return_value=[{"id": "test:1"}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            result = await client.delete("test:1")

            mock_surreal.delete.assert_called_once_with("test:1")
            assert result == [{"id": "test:1"}]

    @pytest.mark.asyncio
    async def test_query_executes_raw_surql(self, mock_surreal: MagicMock) -> None:
        """Test that query() executes raw SurQL and returns results."""
        from codeagent.mcp.db.client import SurrealDBClient

        mock_surreal.query = AsyncMock(return_value=[{"result": [{"id": "test:1"}]}])

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()
            result = await client.query("SELECT * FROM test WHERE id = $id", {"id": "test:1"})

            mock_surreal.query.assert_called_once_with(
                "SELECT * FROM test WHERE id = $id", {"id": "test:1"}
            )
            assert result == [{"result": [{"id": "test:1"}]}]

    @pytest.mark.asyncio
    async def test_default_credentials(self, mock_surreal: MagicMock) -> None:
        """Test that default credentials are used for signin."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()

            mock_surreal.signin.assert_called_once_with(
                {"username": "root", "password": "root"}
            )

    @pytest.mark.asyncio
    async def test_custom_credentials(self, mock_surreal: MagicMock) -> None:
        """Test that custom credentials can be provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient(username="admin", password="secret")
            await client.connect()

            mock_surreal.signin.assert_called_once_with(
                {"username": "admin", "password": "secret"}
            )

    @pytest.mark.asyncio
    async def test_default_namespace_and_database(self, mock_surreal: MagicMock) -> None:
        """Test that default namespace and database are used."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient()
            await client.connect()

            mock_surreal.use.assert_called_once_with("codeagent", "codeagent")

    @pytest.mark.asyncio
    async def test_custom_namespace_and_database(self, mock_surreal: MagicMock) -> None:
        """Test that custom namespace and database can be provided."""
        from codeagent.mcp.db.client import SurrealDBClient

        with patch("codeagent.mcp.db.client.Surreal", return_value=mock_surreal):
            client = SurrealDBClient(namespace="custom_ns", database="custom_db")
            await client.connect()

            mock_surreal.use.assert_called_once_with("custom_ns", "custom_db")
