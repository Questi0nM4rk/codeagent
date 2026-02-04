"""SurrealDB client wrapper for CodeAgent."""

from __future__ import annotations

import asyncio
from pathlib import Path
from types import TracebackType
from typing import Any

from surrealdb import Surreal


class SurrealDBClient:
    """Async wrapper for SurrealDB operations.

    Provides connection management, schema initialization, and CRUD operations.

    Example:
        async with SurrealDBClient() as client:
            await client.initialize_schema(Path("schema.surql"))
            result = await client.create("memory", {"content": "test"})
    """

    def __init__(
        self,
        url: str = "ws://localhost:8000",
        username: str = "root",
        password: str = "root",  # noqa: S107 - Default dev credentials
        namespace: str = "codeagent",
        database: str = "codeagent",
    ) -> None:
        """Initialize the client configuration.

        Args:
            url: SurrealDB WebSocket URL (default: ws://localhost:8000)
            username: Authentication username (default: root)
            password: Authentication password (default: root)
            namespace: SurrealDB namespace to use (default: codeagent)
            database: SurrealDB database to use (default: codeagent)
        """
        self._url = url
        self._username = username
        self._password = password
        self._namespace = namespace
        self._database = database
        self._client = Surreal()

    async def connect(self) -> None:
        """Establish connection to SurrealDB.

        Connects to the server, authenticates, and selects namespace/database.
        Cleans up connection on authentication or namespace selection failure.
        """
        await self._client.connect(self._url)
        try:
            await self._client.signin({"username": self._username, "password": self._password})
            await self._client.use(self._namespace, self._database)
        except Exception:
            await self._client.close()
            raise

    async def close(self) -> None:
        """Close the connection to SurrealDB."""
        await self._client.close()

    async def __aenter__(self) -> SurrealDBClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def initialize_schema(self, schema_path: Path) -> list[Any]:
        """Load and execute a SurQL schema file.

        Args:
            schema_path: Path to the .surql schema file

        Returns:
            List of query results from schema execution
        """
        loop = asyncio.get_running_loop()
        schema_content = await loop.run_in_executor(None, schema_path.read_text)
        return await self._client.query(schema_content)

    async def create(self, table: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Insert a new record into a table.

        Args:
            table: Table name to insert into
            data: Record data as a dictionary

        Returns:
            List containing the created record(s)
        """
        return await self._client.create(table, data)

    async def select(self, thing: str) -> list[dict[str, Any]]:
        """Retrieve records from a table or a specific record by ID.

        Args:
            thing: Table name or record ID (e.g., "memory" or "memory:abc123")

        Returns:
            List of matching records
        """
        return await self._client.select(thing)

    async def update(self, thing: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Update an existing record.

        Args:
            thing: Record ID to update (e.g., "memory:abc123")
            data: New data to merge into the record

        Returns:
            List containing the updated record(s)
        """
        return await self._client.update(thing, data)

    async def delete(self, thing: str) -> list[dict[str, Any]]:
        """Delete a record or all records from a table.

        Args:
            thing: Table name or record ID to delete

        Returns:
            List containing the deleted record(s)
        """
        return await self._client.delete(thing)

    async def query(self, surql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute raw SurQL query.

        Args:
            surql: SurQL query string
            params: Optional query parameters for variable substitution

        Returns:
            List of query results
        """
        return await self._client.query(surql, params)
