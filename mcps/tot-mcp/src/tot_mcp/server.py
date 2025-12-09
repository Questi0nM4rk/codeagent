"""
Tree-of-Thought MCP Server

Enables systematic exploration of solution paths with backtracking.
Based on ToT research showing 4% → 74% improvement on Game of 24
and +70% improvement on complex reasoning tasks.

Tools:
- create_tree: Initialize a new thought tree for a problem
- generate_thoughts: Generate candidate approaches for current state
- evaluate_thoughts: Score thoughts against criteria
- select_path: Choose path(s) to pursue based on strategy
- expand_thought: Expand a specific thought with more detail
- backtrack: Mark current path as failed and return to parent
- get_tree_state: Get current state of the thought tree
- get_best_path: Get the highest-scoring complete path
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "tot",
    instructions="Tree-of-Thought reasoning for systematic solution exploration. "
    "Use this when facing complex problems that benefit from exploring multiple approaches.",
)


class ThoughtStatus(str, Enum):
    """Status of a thought in the tree."""

    PENDING = "pending"  # Not yet evaluated
    PROMISING = "promising"  # Worth pursuing
    UNCERTAIN = "uncertain"  # Might work, needs more exploration
    FAILED = "failed"  # Dead end
    SELECTED = "selected"  # Currently being pursued
    COMPLETE = "complete"  # Reached a solution


@dataclass
class Thought:
    """A node in the thought tree."""

    id: str
    content: str
    rationale: str
    parent_id: str | None = None
    children: list[str] = field(default_factory=list)
    status: ThoughtStatus = ThoughtStatus.PENDING
    scores: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    depth: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtTree:
    """A tree of thoughts for exploring solutions."""

    id: str
    problem: str
    root_id: str
    current_id: str
    thoughts: dict[str, Thought] = field(default_factory=dict)
    criteria: list[str] = field(default_factory=list)
    strategy: str = "greedy"  # greedy, beam, sampling
    max_depth: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# In-memory storage for thought trees
_trees: dict[str, ThoughtTree] = {}


def _get_tree(tree_id: str) -> ThoughtTree | None:
    """Get a thought tree by ID."""
    return _trees.get(tree_id)


def _save_tree(tree: ThoughtTree):
    """Save a thought tree."""
    _trees[tree.id] = tree


@mcp.tool()
def create_tree(
    problem: str,
    criteria: list[str] | None = None,
    strategy: str = "greedy",
    max_depth: int = 5,
) -> dict[str, Any]:
    """
    Initialize a new thought tree for exploring solutions to a problem.

    Args:
        problem: The problem statement to solve
        criteria: Evaluation criteria (default: feasibility, complexity, risk)
        strategy: Selection strategy - 'greedy' (best), 'beam' (top-k), 'sampling' (probabilistic)
        max_depth: Maximum depth of exploration

    Returns:
        Tree ID and initial state
    """
    tree_id = str(uuid4())[:8]
    root_id = str(uuid4())[:8]

    default_criteria = ["feasibility", "complexity", "risk"]
    criteria = criteria or default_criteria

    root = Thought(
        id=root_id,
        content=f"Problem: {problem}",
        rationale="Root node representing the initial problem state",
        status=ThoughtStatus.SELECTED,
        depth=0,
    )

    tree = ThoughtTree(
        id=tree_id,
        problem=problem,
        root_id=root_id,
        current_id=root_id,
        thoughts={root_id: root},
        criteria=criteria,
        strategy=strategy,
        max_depth=max_depth,
    )

    _save_tree(tree)

    return {
        "tree_id": tree_id,
        "problem": problem,
        "criteria": criteria,
        "strategy": strategy,
        "max_depth": max_depth,
        "instruction": f"Generate {3} distinct approaches to solve this problem. "
        f"For each approach, provide: content (the approach), rationale (why it might work). "
        f"Consider tradeoffs for criteria: {', '.join(criteria)}",
    }


@mcp.tool()
def generate_thoughts(
    tree_id: str,
    thoughts: list[dict[str, str]],
) -> dict[str, Any]:
    """
    Add candidate thoughts (approaches) to the current node.

    Args:
        tree_id: ID of the thought tree
        thoughts: List of thoughts, each with 'content' and 'rationale' keys

    Returns:
        Added thought IDs and next instruction
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    current = tree.thoughts[tree.current_id]
    added = []

    for thought_data in thoughts:
        thought_id = str(uuid4())[:8]
        thought = Thought(
            id=thought_id,
            content=thought_data.get("content", ""),
            rationale=thought_data.get("rationale", ""),
            parent_id=current.id,
            depth=current.depth + 1,
        )
        tree.thoughts[thought_id] = thought
        current.children.append(thought_id)
        added.append({"id": thought_id, "content": thought.content[:100]})

    _save_tree(tree)

    return {
        "tree_id": tree_id,
        "parent_id": current.id,
        "added": added,
        "instruction": f"Now evaluate each thought on criteria: {', '.join(tree.criteria)}. "
        f"Score each criterion 1-10. Call evaluate_thoughts with the scores.",
    }


@mcp.tool()
def evaluate_thoughts(
    tree_id: str,
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Evaluate thoughts against criteria.

    Args:
        tree_id: ID of the thought tree
        evaluations: List of {thought_id, scores: {criterion: score}}

    Returns:
        Evaluated thoughts with classifications
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    results = []

    for eval_data in evaluations:
        thought_id = eval_data.get("thought_id")
        scores = eval_data.get("scores", {})

        if thought_id not in tree.thoughts:
            continue

        thought = tree.thoughts[thought_id]
        thought.scores = scores

        # Calculate total score (average)
        if scores:
            thought.total_score = sum(scores.values()) / len(scores)

        # Classify based on scores
        min_score = min(scores.values()) if scores else 0
        if min_score >= 7:
            thought.status = ThoughtStatus.PROMISING
            classification = "promising"
        elif min_score >= 4:
            thought.status = ThoughtStatus.UNCERTAIN
            classification = "uncertain"
        else:
            thought.status = ThoughtStatus.FAILED
            classification = "failed"

        results.append(
            {
                "thought_id": thought_id,
                "content": thought.content[:100],
                "scores": scores,
                "total_score": round(thought.total_score, 2),
                "classification": classification,
            }
        )

    _save_tree(tree)

    # Sort by total score
    results.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "tree_id": tree_id,
        "evaluated": results,
        "instruction": f"Using {tree.strategy} strategy, call select_path to choose which approach(es) to pursue.",
    }


@mcp.tool()
def select_path(
    tree_id: str,
    thought_id: str | None = None,
    beam_width: int = 3,
) -> dict[str, Any]:
    """
    Select the best thought(s) to pursue based on strategy.

    Args:
        tree_id: ID of the thought tree
        thought_id: Specific thought to select (optional, uses strategy if not provided)
        beam_width: For beam strategy, how many paths to keep

    Returns:
        Selected thought(s) and next steps
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    current = tree.thoughts[tree.current_id]

    # Get children that aren't failed
    candidates = [
        tree.thoughts[cid]
        for cid in current.children
        if tree.thoughts[cid].status != ThoughtStatus.FAILED
    ]

    if not candidates:
        return {
            "tree_id": tree_id,
            "message": "No viable candidates. Consider backtracking.",
            "instruction": "Call backtrack with a reason to return to parent node.",
        }

    # Sort by score
    candidates.sort(key=lambda t: t.total_score, reverse=True)

    if thought_id:
        # Manual selection
        selected = [tree.thoughts.get(thought_id)]
        if not selected[0]:
            return {"error": f"Thought not found: {thought_id}"}
    elif tree.strategy == "greedy":
        selected = [candidates[0]]
    elif tree.strategy == "beam":
        selected = candidates[:beam_width]
    else:  # sampling
        # Simple implementation: take top candidates
        selected = candidates[:beam_width]

    # Mark as selected and update current
    for thought in selected:
        thought.status = ThoughtStatus.SELECTED

    # Move to first selected
    tree.current_id = selected[0].id
    _save_tree(tree)

    at_max_depth = selected[0].depth >= tree.max_depth

    return {
        "tree_id": tree_id,
        "selected": [
            {
                "id": t.id,
                "content": t.content,
                "score": round(t.total_score, 2),
                "depth": t.depth,
            }
            for t in selected
        ],
        "current_depth": selected[0].depth,
        "max_depth": tree.max_depth,
        "at_max_depth": at_max_depth,
        "instruction": (
            "Maximum depth reached. Evaluate if this is a complete solution. "
            "If yes, call get_best_path. If not satisfactory, call backtrack."
            if at_max_depth
            else f"Expand the selected thought. Generate {3} more specific sub-approaches "
            f"that implement or refine this approach."
        ),
    }


@mcp.tool()
def expand_thought(
    tree_id: str,
    thought_id: str,
    expansion: str,
    implementation_notes: str = "",
) -> dict[str, Any]:
    """
    Expand a thought with more detailed content.

    Args:
        tree_id: ID of the thought tree
        thought_id: ID of the thought to expand
        expansion: Detailed expansion of the thought
        implementation_notes: Optional notes about implementation

    Returns:
        Updated thought state
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    if thought_id not in tree.thoughts:
        return {"error": f"Thought not found: {thought_id}"}

    thought = tree.thoughts[thought_id]
    thought.metadata["expansion"] = expansion
    thought.metadata["implementation_notes"] = implementation_notes
    thought.status = ThoughtStatus.COMPLETE

    _save_tree(tree)

    return {
        "tree_id": tree_id,
        "thought_id": thought_id,
        "status": "expanded",
        "depth": thought.depth,
        "instruction": "Thought expanded. Generate child thoughts to further refine, or call get_best_path if done.",
    }


@mcp.tool()
def backtrack(
    tree_id: str,
    reason: str,
) -> dict[str, Any]:
    """
    Mark current path as failed and return to parent node.

    Args:
        tree_id: ID of the thought tree
        reason: Why this path failed

    Returns:
        New current position and available alternatives
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    current = tree.thoughts[tree.current_id]
    current.status = ThoughtStatus.FAILED
    current.metadata["failure_reason"] = reason

    if not current.parent_id:
        return {
            "tree_id": tree_id,
            "message": "At root node, cannot backtrack further.",
            "instruction": "Generate new initial approaches with generate_thoughts.",
        }

    # Move to parent
    tree.current_id = current.parent_id
    parent = tree.thoughts[current.parent_id]
    _save_tree(tree)

    # Find siblings that haven't failed
    siblings = [
        tree.thoughts[cid]
        for cid in parent.children
        if tree.thoughts[cid].status != ThoughtStatus.FAILED and cid != current.id
    ]

    return {
        "tree_id": tree_id,
        "backtracked_from": current.id,
        "reason": reason,
        "current_id": parent.id,
        "current_depth": parent.depth,
        "alternatives": [
            {"id": s.id, "content": s.content[:80], "score": round(s.total_score, 2)}
            for s in sorted(siblings, key=lambda t: t.total_score, reverse=True)
        ],
        "instruction": (
            "Select an alternative path with select_path, or generate new thoughts."
            if siblings
            else "No alternatives at this level. Backtrack further or generate new approaches."
        ),
    }


@mcp.tool()
def get_tree_state(tree_id: str) -> dict[str, Any]:
    """
    Get the current state of the thought tree.

    Args:
        tree_id: ID of the thought tree

    Returns:
        Full tree state including all thoughts and their relationships
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    current = tree.thoughts[tree.current_id]

    # Build tree visualization
    def build_node(thought_id: str, indent: int = 0) -> list[str]:
        thought = tree.thoughts[thought_id]
        prefix = "  " * indent
        status_icon = {
            ThoughtStatus.PENDING: "○",
            ThoughtStatus.PROMISING: "✓",
            ThoughtStatus.UNCERTAIN: "?",
            ThoughtStatus.FAILED: "✗",
            ThoughtStatus.SELECTED: "→",
            ThoughtStatus.COMPLETE: "★",
        }[thought.status]

        lines = [f"{prefix}{status_icon} [{thought.id}] {thought.content[:60]}... (score: {thought.total_score:.1f})"]

        for child_id in thought.children:
            lines.extend(build_node(child_id, indent + 1))

        return lines

    visualization = "\n".join(build_node(tree.root_id))

    return {
        "tree_id": tree_id,
        "problem": tree.problem,
        "strategy": tree.strategy,
        "criteria": tree.criteria,
        "current": {
            "id": current.id,
            "content": current.content,
            "depth": current.depth,
            "status": current.status.value,
        },
        "total_thoughts": len(tree.thoughts),
        "max_depth": tree.max_depth,
        "visualization": visualization,
    }


@mcp.tool()
def get_best_path(tree_id: str) -> dict[str, Any]:
    """
    Get the highest-scoring path through the tree.

    Args:
        tree_id: ID of the thought tree

    Returns:
        Best path from root to leaf with all thoughts and rationale
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    # Find best leaf (highest score, preferably complete or promising)
    best_leaf = None
    best_score = -1

    for thought in tree.thoughts.values():
        if not thought.children:  # Is a leaf
            # Prefer complete/promising over failed
            status_bonus = {
                ThoughtStatus.COMPLETE: 100,
                ThoughtStatus.PROMISING: 50,
                ThoughtStatus.SELECTED: 25,
                ThoughtStatus.UNCERTAIN: 10,
                ThoughtStatus.PENDING: 0,
                ThoughtStatus.FAILED: -100,
            }[thought.status]

            effective_score = thought.total_score + status_bonus
            if effective_score > best_score:
                best_score = effective_score
                best_leaf = thought

    if not best_leaf:
        return {
            "tree_id": tree_id,
            "message": "No complete paths found.",
            "instruction": "Continue exploration with generate_thoughts.",
        }

    # Build path from root to best leaf
    path = []
    current = best_leaf
    while current:
        path.append(
            {
                "id": current.id,
                "depth": current.depth,
                "content": current.content,
                "rationale": current.rationale,
                "scores": current.scores,
                "total_score": round(current.total_score, 2),
                "status": current.status.value,
                "expansion": current.metadata.get("expansion"),
                "implementation_notes": current.metadata.get("implementation_notes"),
            }
        )
        current = tree.thoughts.get(current.parent_id) if current.parent_id else None

    path.reverse()

    return {
        "tree_id": tree_id,
        "problem": tree.problem,
        "path_length": len(path),
        "total_score": round(best_leaf.total_score, 2),
        "path": path,
        "summary": " → ".join(p["content"][:50] for p in path),
    }


@mcp.tool()
def list_trees() -> dict[str, Any]:
    """
    List all active thought trees.

    Returns:
        List of tree summaries
    """
    trees = []
    for tree in _trees.values():
        current = tree.thoughts[tree.current_id]
        trees.append(
            {
                "id": tree.id,
                "problem": tree.problem[:80],
                "thoughts": len(tree.thoughts),
                "current_depth": current.depth,
                "max_depth": tree.max_depth,
                "created": tree.created_at,
            }
        )

    return {"trees": trees, "count": len(trees)}


def main():
    """Entry point for the tot MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
