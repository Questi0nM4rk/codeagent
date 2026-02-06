"""SurrealDB client wrapper for CodeAgent."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

from surrealdb import AsyncSurreal

_DEFAULT_URL = "ws://localhost:8000"
_DEFAULT_NS = "codeagent"
_DEFAULT_DB = "codeagent"


class SurrealDBClient:
    """Async wrapper for SurrealDB operations.

    Provides connection management, schema initialization,
    and CRUD operations.

    Credentials are resolved from environment variables
    SURREALDB_USER / SURREALDB_PASS, falling back to
    "root"/"root" for local development.

    Example:
        async with SurrealDBClient() as client:
            await client.initialize_schema(Path("schema.surql"))
            result = await client.create("memory", {"content": "test"})
    """

    def __init__(
        self,
        url: str = _DEFAULT_URL,
        username: str | None = None,
        password: str | None = None,
        namespace: str = _DEFAULT_NS,
        database: str = _DEFAULT_DB,
    ) -> None:
        """Initialize the client configuration.

        Args:
            url: SurrealDB WebSocket URL
            username: Auth username (env: SURREALDB_USER)
            password: Auth password (env: SURREALDB_PASS)
            namespace: SurrealDB namespace to use
            database: SurrealDB database to use
        """
        self._url = url
        self._username = username or os.environ.get("SURREALDB_USER", "root")
        self._password = password or os.environ.get("SURREALDB_PASS", "root")
        self._namespace = namespace
        self._database = database
        self._client = AsyncSurreal(self._url)

    async def connect(self) -> None:
        """Establish connection to SurrealDB.

        Connects to the server, authenticates, and selects namespace/database.
        Cleans up connection on authentication or namespace selection failure.
        """
        await self._client.connect(self._url)
        try:
            await self._client.signin(
                {"username": self._username, "password": self._password},
            )
            await self._client.use(self._namespace, self._database)
        except Exception:
            await self._client.close()
            raise

    async def close(self) -> None:
        """Close the connection to SurrealDB."""
        await self._client.close()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def initialize_schema(self, schema_path: Path) -> Any:
        """Load and execute a SurQL schema file.

        Args:
            schema_path: Path to the .surql schema file

        Returns:
            Query results from schema execution
        """
        loop = asyncio.get_running_loop()
        schema_content = await loop.run_in_executor(None, schema_path.read_text)
        return await self._client.query(schema_content)

    async def create(self, table: str, data: dict[str, Any]) -> Any:
        """Insert a new record into a table.

        Args:
            table: Table name to insert into
            data: Record data as a dictionary

        Returns:
            The created record(s) from SurrealDB
        """
        return await self._client.create(table, data)

    async def select(self, thing: str) -> Any:
        """Retrieve records from a table or a specific record by ID.

        Args:
            thing: Table name or record ID (e.g., "memory" or "memory:abc123")

        Returns:
            Matching records from SurrealDB
        """
        return await self._client.select(thing)

    async def update(self, thing: str, data: dict[str, Any]) -> Any:
        """Update an existing record.

        Args:
            thing: Record ID to update (e.g., "memory:abc123")
            data: New data to merge into the record

        Returns:
            The updated record(s) from SurrealDB
        """
        return await self._client.update(thing, data)

    async def delete(self, thing: str) -> Any:
        """Delete a record or all records from a table.

        Args:
            thing: Table name or record ID to delete

        Returns:
            The deleted record(s) from SurrealDB
        """
        return await self._client.delete(thing)

    async def query(self, surql: str, params: dict[str, Any] | None = None) -> Any:
        """Execute raw SurQL query.

        Args:
            surql: SurQL query string
            params: Optional query parameters for variable substitution

        Returns:
            Query results from SurrealDB
        """
        return await self._client.query(surql, params)
