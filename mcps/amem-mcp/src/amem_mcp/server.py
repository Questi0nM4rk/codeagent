"""
A-MEM MCP Server - Brain-like Memory for Claude Code

Based on NeurIPS 2025 paper "A-MEM: Agentic Memory for LLM Agents"
Implements Zettelkasten-inspired memory with dynamic linking and evolution.

Features:
- Automatic memory linking (new memories connect to related existing ones)
- Memory evolution (new info updates existing memory context)
- Rich metadata generation (keywords, context, tags)
- Global memory shared across all projects

Tools:
- store_memory: Store knowledge with automatic linking and evolution
- search_memory: Semantic search across all memories
- read_memory: Read specific memory by ID with full metadata
- list_memories: List recent memories with filtering
- update_memory: Update existing memory (triggers re-evolution)
- delete_memory: Remove a memory
- get_memory_stats: Statistics about the memory system
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistent storage directory (global - shared across all projects)
DATA_DIR = Path(os.environ.get("CODEAGENT_HOME", Path.home() / ".codeagent")) / "memory"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP(
    "amem",
    instructions="Brain-like memory for Claude Code using A-MEM architecture. "
    "Memories automatically link to each other and evolve over time. "
    "Use this for storing and retrieving project knowledge, patterns, and decisions.",
)

# Global memory system instance (lazy loaded)
_memory_system = None
_use_fallback = False


def _get_memory_system():
    """Get or initialize the memory system."""
    global _memory_system, _use_fallback

    if _memory_system is not None:
        return _memory_system

    try:
        from agentic_memory.memory_system import AgenticMemorySystem

        # Check for API key
        openai_key = os.environ.get("OPENAI_API_KEY", "")

        if openai_key:
            # Use OpenAI for metadata generation
            _memory_system = AgenticMemorySystem(
                model_name='all-MiniLM-L6-v2',  # Local embeddings (free)
                llm_backend="openai",
                llm_model="gpt-4o-mini",
                persist_directory=str(DATA_DIR / "chromadb"),
            )
            logger.info("Initialized A-MEM with OpenAI backend")
        else:
            # Try Ollama for local inference
            try:
                _memory_system = AgenticMemorySystem(
                    model_name='all-MiniLM-L6-v2',
                    llm_backend="ollama",
                    llm_model="llama2",
                    persist_directory=str(DATA_DIR / "chromadb"),
                )
                logger.info("Initialized A-MEM with Ollama backend")
            except Exception:
                # Fallback to simple mode without LLM metadata
                _use_fallback = True
                _memory_system = _SimpleFallbackMemory()
                logger.warning("Initialized A-MEM in fallback mode (no LLM)")

        return _memory_system

    except ImportError as e:
        logger.warning(f"A-MEM not installed, using fallback: {e}")
        _use_fallback = True
        _memory_system = _SimpleFallbackMemory()
        return _memory_system


class _SimpleFallbackMemory:
    """
    Simple fallback memory when A-MEM is not available.
    Stores memories in JSON with basic keyword extraction.
    """

    def __init__(self):
        self.storage_file = DATA_DIR / "memories.json"
        self.memories = self._load()

    def _load(self) -> dict:
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {"memories": {}, "counter": 0}
        return {"memories": {}, "counter": 0}

    def _save(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.memories, f, indent=2)

    def _extract_keywords(self, text: str) -> list[str]:
        """Simple keyword extraction."""
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                     'and', 'but', 'or', 'not', 'this', 'that', 'it', 'its'}
        words = text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w.strip('.,!?;:') not in stopwords and len(w) > 2]
        return list(set(keywords))[:10]

    def _find_links(self, keywords: list[str]) -> list[str]:
        """Find related memories based on keyword overlap."""
        links = []
        for mem_id, mem in self.memories.get("memories", {}).items():
            mem_keywords = set(mem.get("keywords", []))
            overlap = len(set(keywords) & mem_keywords)
            if overlap >= 2:  # At least 2 keywords in common
                links.append(mem_id)
        return links[:5]  # Max 5 links

    def add_note(self, content: str, tags: list = None, **kwargs) -> str:
        """Add a new memory."""
        self.memories["counter"] = self.memories.get("counter", 0) + 1
        mem_id = f"mem_{self.memories['counter']:04d}"

        keywords = self._extract_keywords(content)
        links = self._find_links(keywords)

        memory = {
            "id": mem_id,
            "content": content,
            "keywords": keywords,
            "tags": tags or [],
            "context": f"Memory added on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "links": links,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self.memories.setdefault("memories", {})[mem_id] = memory
        self._save()

        return mem_id

    def read(self, memory_id: str):
        """Read a memory by ID."""
        mem = self.memories.get("memories", {}).get(memory_id)
        if not mem:
            return None

        # Return as object-like dict
        class MemoryNote:
            def __init__(self, data):
                self.id = data["id"]
                self.content = data["content"]
                self.keywords = data["keywords"]
                self.tags = data["tags"]
                self.context = data["context"]
                self.links = data.get("links", [])
                self.created_at = data["created_at"]

        return MemoryNote(mem)

    def search_agentic(self, query: str, k: int = 5) -> list[dict]:
        """Search memories by keyword overlap."""
        query_keywords = set(self._extract_keywords(query))

        scored = []
        for mem_id, mem in self.memories.get("memories", {}).items():
            mem_keywords = set(mem.get("keywords", []))
            mem_content = mem.get("content", "").lower()

            # Score by keyword overlap and content match
            keyword_score = len(query_keywords & mem_keywords) / max(len(query_keywords), 1)
            content_score = sum(1 for kw in query_keywords if kw in mem_content) / max(len(query_keywords), 1)
            score = keyword_score * 0.6 + content_score * 0.4

            if score > 0:
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, mem in scored[:k]:
            results.append({
                "id": mem["id"],
                "content": mem["content"],
                "keywords": mem["keywords"],
                "tags": mem["tags"],
                "context": mem.get("context", ""),
                "links": mem.get("links", []),
                "score": round(score, 3),
            })

        return results

    def update(self, memory_id: str, content: str = None, **kwargs):
        """Update a memory."""
        if memory_id not in self.memories.get("memories", {}):
            return False

        if content:
            self.memories["memories"][memory_id]["content"] = content
            self.memories["memories"][memory_id]["keywords"] = self._extract_keywords(content)
            self.memories["memories"][memory_id]["links"] = self._find_links(
                self.memories["memories"][memory_id]["keywords"]
            )

        self.memories["memories"][memory_id]["updated_at"] = datetime.now().isoformat()
        self._save()
        return True

    def delete(self, memory_id: str):
        """Delete a memory."""
        if memory_id in self.memories.get("memories", {}):
            del self.memories["memories"][memory_id]
            self._save()
            return True
        return False


def _format_note(note) -> dict:
    """Format a memory note for response."""
    return {
        "id": note.id if hasattr(note, 'id') else note.get("id", ""),
        "content": note.content if hasattr(note, 'content') else note.get("content", ""),
        "keywords": note.keywords if hasattr(note, 'keywords') else note.get("keywords", []),
        "tags": note.tags if hasattr(note, 'tags') else note.get("tags", []),
        "context": note.context if hasattr(note, 'context') else note.get("context", ""),
        "links": note.links if hasattr(note, 'links') else note.get("links", []),
    }


@mcp.tool()
def store_memory(
    content: str,
    tags: list[str] | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    """
    Store knowledge with automatic linking and memory evolution.

    The memory system will:
    1. Auto-generate keywords, context, and tags
    2. Find related existing memories and link them
    3. Update existing memories with new context (evolution)

    Args:
        content: The knowledge to store (patterns, decisions, insights)
        tags: Optional tags for categorization (e.g., ["architecture", "pattern"])
        project: Optional project name for filtering later

    Returns:
        Stored memory ID with generated metadata and links
    """
    memory = _get_memory_system()

    # Add project as tag if provided
    all_tags = list(tags) if tags else []
    if project:
        all_tags.append(f"project:{project}")

    try:
        memory_id = memory.add_note(content=content, tags=all_tags)

        # Read back to get generated metadata
        note = memory.read(memory_id)

        if note:
            return {
                "stored": True,
                "memory_id": memory_id,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "keywords": _format_note(note).get("keywords", []),
                "context": _format_note(note).get("context", ""),
                "linked_to": len(_format_note(note).get("links", [])),
                "using_fallback": _use_fallback,
                "storage_path": str(DATA_DIR),
            }
        else:
            return {
                "stored": True,
                "memory_id": memory_id,
                "content_preview": content[:100],
                "using_fallback": _use_fallback,
            }

    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return {
            "stored": False,
            "error": str(e),
        }


@mcp.tool()
def search_memory(
    query: str,
    k: int = 5,
    project: str | None = None,
) -> dict[str, Any]:
    """
    Semantic search across all memories.

    Finds memories related to your query using vector similarity
    and the Zettelkasten link structure.

    Args:
        query: What to search for (natural language)
        k: Maximum results to return (default 5)
        project: Optional filter by project name

    Returns:
        Relevant memories with content, keywords, context, and links
    """
    memory = _get_memory_system()
    k = min(max(k, 1), 20)

    try:
        results = memory.search_agentic(query, k=k)

        # Filter by project if specified
        if project:
            project_tag = f"project:{project}"
            results = [r for r in results if project_tag in r.get("tags", [])]

        formatted = []
        for result in results:
            formatted.append({
                "id": result.get("id", ""),
                "content": result.get("content", ""),
                "keywords": result.get("keywords", []),
                "tags": result.get("tags", []),
                "context": result.get("context", ""),
                "links": result.get("links", []),
                "relevance": result.get("score", 0),
            })

        return {
            "query": query,
            "results": formatted,
            "count": len(formatted),
            "using_fallback": _use_fallback,
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e),
        }


@mcp.tool()
def read_memory(memory_id: str) -> dict[str, Any]:
    """
    Read a specific memory by ID with full metadata.

    Args:
        memory_id: The memory ID to retrieve

    Returns:
        Full memory content with keywords, context, tags, and links
    """
    memory = _get_memory_system()

    try:
        note = memory.read(memory_id)

        if note:
            formatted = _format_note(note)
            formatted["found"] = True
            return formatted
        else:
            return {
                "found": False,
                "error": f"Memory not found: {memory_id}",
            }

    except Exception as e:
        return {
            "found": False,
            "error": str(e),
        }


@mcp.tool()
def list_memories(
    limit: int = 10,
    project: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    """
    List recent memories with optional filtering.

    Args:
        limit: Maximum memories to return (default 10)
        project: Filter by project name
        tag: Filter by tag

    Returns:
        List of recent memories
    """
    memory = _get_memory_system()
    limit = min(max(limit, 1), 50)

    try:
        # Use search with empty query to get all, then filter
        results = memory.search_agentic("", k=limit * 2)  # Get more to account for filtering

        # Filter
        if project:
            project_tag = f"project:{project}"
            results = [r for r in results if project_tag in r.get("tags", [])]

        if tag:
            results = [r for r in results if tag in r.get("tags", [])]

        results = results[:limit]

        return {
            "memories": [{
                "id": r.get("id", ""),
                "content_preview": r.get("content", "")[:100],
                "keywords": r.get("keywords", [])[:5],
                "tags": r.get("tags", []),
            } for r in results],
            "count": len(results),
            "filters": {
                "project": project,
                "tag": tag,
            },
        }

    except Exception as e:
        return {
            "memories": [],
            "count": 0,
            "error": str(e),
        }


@mcp.tool()
def update_memory(
    memory_id: str,
    content: str,
) -> dict[str, Any]:
    """
    Update an existing memory. Triggers re-evolution of links.

    Args:
        memory_id: The memory to update
        content: New content

    Returns:
        Updated memory details
    """
    memory = _get_memory_system()

    try:
        result = memory.update(memory_id, content=content)

        if result:
            note = memory.read(memory_id)
            if note:
                return {
                    "updated": True,
                    "memory_id": memory_id,
                    "new_keywords": _format_note(note).get("keywords", []),
                    "new_links": len(_format_note(note).get("links", [])),
                }

        return {
            "updated": False,
            "error": f"Memory not found: {memory_id}",
        }

    except Exception as e:
        return {
            "updated": False,
            "error": str(e),
        }


@mcp.tool()
def delete_memory(memory_id: str) -> dict[str, Any]:
    """
    Delete a memory.

    Args:
        memory_id: The memory to delete

    Returns:
        Confirmation of deletion
    """
    memory = _get_memory_system()

    try:
        result = memory.delete(memory_id)
        return {
            "deleted": bool(result),
            "memory_id": memory_id,
        }
    except Exception as e:
        return {
            "deleted": False,
            "error": str(e),
        }


@mcp.tool()
def get_memory_stats() -> dict[str, Any]:
    """
    Get statistics about the memory system.

    Returns:
        Statistics including total memories, storage info, and system status
    """
    memory = _get_memory_system()

    try:
        # Count memories by doing a broad search
        all_results = memory.search_agentic("", k=1000)
        total = len(all_results)

        # Count by project
        projects = {}
        tags_count = {}
        for r in all_results:
            for tag in r.get("tags", []):
                if tag.startswith("project:"):
                    proj = tag[8:]
                    projects[proj] = projects.get(proj, 0) + 1
                else:
                    tags_count[tag] = tags_count.get(tag, 0) + 1

        return {
            "total_memories": total,
            "memories_by_project": projects,
            "top_tags": dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "storage_path": str(DATA_DIR),
            "using_fallback": _use_fallback,
            "backend": "fallback" if _use_fallback else "A-MEM",
        }

    except Exception as e:
        return {
            "error": str(e),
            "storage_path": str(DATA_DIR),
            "using_fallback": _use_fallback,
        }


def main():
    """Entry point for the A-MEM MCP server."""
    logger.info(f"Starting A-MEM MCP server, storage: {DATA_DIR}")
    mcp.run()


if __name__ == "__main__":
    main()
