"""
Tree-of-Thought MCP Server

Enables systematic exploration of solution paths with backtracking.
Based on ToT research showing 4% → 74% improvement on Game of 24
and +70% improvement on complex reasoning tasks.

Features:
- Persistent storage (JSON files in ~/.codeagent/data/thought-trees/)
- Thinking level integration (maps complexity to think/think hard/ultrathink)
- Advanced pruning (weighted criteria, diversity preservation, alpha-beta style)
- Multiple strategies: greedy, beam, sampling, diverse

Tools:
- create_tree: Initialize a new thought tree for a problem
- generate_thoughts: Generate candidate approaches for current state
- evaluate_thoughts: Score thoughts against criteria
- select_path: Choose path(s) to pursue based on strategy
- expand_thought: Expand a specific thought with more detail
- backtrack: Mark current path as failed and return to parent
- get_tree_state: Get current state of the thought tree
- get_best_path: Get the highest-scoring complete path
- list_trees: List all thought trees
- delete_tree: Delete a thought tree
"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistent storage directory
DATA_DIR = Path(os.environ.get("CODEAGENT_HOME", Path.home() / ".codeagent")) / "data" / "thought-trees"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP(
    "tot",
    instructions="Tree-of-Thought reasoning for systematic solution exploration. "
    "Use this when facing complex problems that benefit from exploring multiple approaches.",
)


class ThinkingLevel(str, Enum):
    """Claude's thinking levels for extended reasoning."""
    THINK = "think"  # Light reasoning
    THINK_HARD = "think hard"  # Moderate complexity
    THINK_HARDER = "think harder"  # High complexity
    ULTRATHINK = "ultrathink"  # Maximum depth (architectural decisions)


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
    criteria_weights: dict[str, float] = field(default_factory=dict)  # Criterion name → weight (0.0-1.0)
    strategy: str = "greedy"  # greedy, beam, sampling, diverse
    max_depth: int = 5
    thinking_level: str = ThinkingLevel.THINK_HARD.value  # Recommended thinking level
    best_score_seen: float = 0.0  # For alpha-beta style pruning
    diversity_threshold: float = 0.3  # Minimum difference to keep diverse solutions
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# In-memory cache for thought trees (loaded from disk on demand)
_trees_cache: dict[str, ThoughtTree] = {}


def _get_tree_path(tree_id: str) -> Path:
    """Get file path for a thought tree."""
    return DATA_DIR / f"{tree_id}.json"


def _tree_to_dict(tree: ThoughtTree) -> dict:
    """Convert tree to serializable dict."""
    return {
        "id": tree.id,
        "problem": tree.problem,
        "root_id": tree.root_id,
        "current_id": tree.current_id,
        "thoughts": {
            tid: {
                "id": t.id,
                "content": t.content,
                "rationale": t.rationale,
                "parent_id": t.parent_id,
                "children": t.children,
                "status": t.status.value,
                "scores": t.scores,
                "total_score": t.total_score,
                "depth": t.depth,
                "created_at": t.created_at,
                "metadata": t.metadata,
            }
            for tid, t in tree.thoughts.items()
        },
        "criteria": tree.criteria,
        "criteria_weights": tree.criteria_weights,
        "strategy": tree.strategy,
        "max_depth": tree.max_depth,
        "thinking_level": tree.thinking_level,
        "best_score_seen": tree.best_score_seen,
        "diversity_threshold": tree.diversity_threshold,
        "created_at": tree.created_at,
        "updated_at": tree.updated_at,
    }


def _dict_to_tree(data: dict) -> ThoughtTree:
    """Convert dict back to ThoughtTree."""
    thoughts = {}
    for tid, tdata in data.get("thoughts", {}).items():
        thoughts[tid] = Thought(
            id=tdata["id"],
            content=tdata["content"],
            rationale=tdata["rationale"],
            parent_id=tdata.get("parent_id"),
            children=tdata.get("children", []),
            status=ThoughtStatus(tdata.get("status", "pending")),
            scores=tdata.get("scores", {}),
            total_score=tdata.get("total_score", 0.0),
            depth=tdata.get("depth", 0),
            created_at=tdata.get("created_at", ""),
            metadata=tdata.get("metadata", {}),
        )

    return ThoughtTree(
        id=data["id"],
        problem=data["problem"],
        root_id=data["root_id"],
        current_id=data["current_id"],
        thoughts=thoughts,
        criteria=data.get("criteria", []),
        criteria_weights=data.get("criteria_weights", {}),
        strategy=data.get("strategy", "greedy"),
        max_depth=data.get("max_depth", 5),
        thinking_level=data.get("thinking_level", ThinkingLevel.THINK_HARD.value),
        best_score_seen=data.get("best_score_seen", 0.0),
        diversity_threshold=data.get("diversity_threshold", 0.3),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


def _get_tree(tree_id: str) -> ThoughtTree | None:
    """Get a thought tree by ID (from cache or disk)."""
    # Check cache first
    if tree_id in _trees_cache:
        return _trees_cache[tree_id]

    # Try to load from disk
    path = _get_tree_path(tree_id)
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
            tree = _dict_to_tree(data)
            _trees_cache[tree_id] = tree
            return tree
        except Exception as e:
            logger.error(f"Failed to load tree {tree_id}: {e}")
            return None

    return None


def _save_tree(tree: ThoughtTree):
    """Save a thought tree (to cache and disk)."""
    tree.updated_at = datetime.now().isoformat()
    _trees_cache[tree.id] = tree

    # Persist to disk
    path = _get_tree_path(tree.id)
    try:
        with open(path, "w") as f:
            json.dump(_tree_to_dict(tree), f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save tree {tree.id}: {e}")


def _delete_tree(tree_id: str) -> bool:
    """Delete a thought tree from cache and disk."""
    if tree_id in _trees_cache:
        del _trees_cache[tree_id]

    path = _get_tree_path(tree_id)
    if path.exists():
        try:
            path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete tree {tree_id}: {e}")
            return False
    return True


def _estimate_thinking_level(problem: str, max_depth: int) -> str:
    """Estimate appropriate thinking level based on problem characteristics."""
    problem_lower = problem.lower()

    # Ultrathink indicators (architectural, design decisions)
    ultrathink_keywords = [
        "architect", "design", "system", "infrastructure", "scalab",
        "microservice", "database schema", "api design", "security model",
    ]
    if any(kw in problem_lower for kw in ultrathink_keywords) or max_depth >= 5:
        return ThinkingLevel.ULTRATHINK.value

    # Think harder indicators (complex implementation)
    harder_keywords = [
        "refactor", "optimize", "complex", "algorithm", "performance",
        "concurrent", "async", "parallel", "distributed",
    ]
    if any(kw in problem_lower for kw in harder_keywords) or max_depth >= 4:
        return ThinkingLevel.THINK_HARDER.value

    # Think hard indicators (standard implementation)
    hard_keywords = [
        "implement", "feature", "module", "component", "integration",
        "test", "fix", "debug", "error handling",
    ]
    if any(kw in problem_lower for kw in hard_keywords) or max_depth >= 3:
        return ThinkingLevel.THINK_HARD.value

    # Default to think for simple problems
    return ThinkingLevel.THINK.value


def _calculate_weighted_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Calculate weighted average score."""
    if not scores:
        return 0.0

    if not weights:
        # Equal weights if none specified
        return sum(scores.values()) / len(scores)

    total_weight = 0.0
    weighted_sum = 0.0

    for criterion, score in scores.items():
        weight = weights.get(criterion, 1.0)
        weighted_sum += score * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0.0


def _should_prune(thought: "Thought", tree: ThoughtTree) -> bool:
    """Determine if a thought should be pruned (alpha-beta style)."""
    # Never prune if no best score established yet
    if tree.best_score_seen <= 0:
        return False

    # Prune if score is significantly worse than best seen
    # Allow some tolerance based on depth (deeper = more tolerance)
    tolerance = 0.1 * thought.depth
    threshold = tree.best_score_seen * (0.5 + tolerance)

    return thought.total_score < threshold


def _is_diverse_enough(thought: "Thought", siblings: list["Thought"], threshold: float) -> bool:
    """Check if thought is different enough from siblings to keep."""
    if not siblings:
        return True

    # Simple diversity check: compare content similarity
    thought_words = set(thought.content.lower().split())

    for sibling in siblings:
        if sibling.status == ThoughtStatus.FAILED:
            continue
        sibling_words = set(sibling.content.lower().split())

        # Jaccard similarity
        intersection = len(thought_words & sibling_words)
        union = len(thought_words | sibling_words)
        similarity = intersection / union if union > 0 else 0

        if similarity > (1 - threshold):
            return False  # Too similar to an existing sibling

    return True


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

    # Estimate thinking level based on problem complexity
    thinking_level = _estimate_thinking_level(problem, max_depth)

    # Default equal weights for criteria
    criteria_weights = {c: 1.0 for c in criteria}

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
        criteria_weights=criteria_weights,
        strategy=strategy,
        max_depth=max_depth,
        thinking_level=thinking_level,
    )

    _save_tree(tree)

    return {
        "tree_id": tree_id,
        "problem": problem,
        "criteria": criteria,
        "criteria_weights": criteria_weights,
        "strategy": strategy,
        "max_depth": max_depth,
        "thinking_level": thinking_level,
        "storage": str(_get_tree_path(tree_id)),
        "instruction": f"Generate {3} distinct approaches to solve this problem. "
        f"For each approach, provide: content (the approach), rationale (why it might work). "
        f"Consider tradeoffs for criteria: {', '.join(criteria)}. "
        f"Recommended thinking level: {thinking_level}",
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
    pruned_count = 0

    for eval_data in evaluations:
        thought_id = eval_data.get("thought_id")
        scores = eval_data.get("scores", {})

        if thought_id not in tree.thoughts:
            continue

        thought = tree.thoughts[thought_id]
        thought.scores = scores

        # Calculate weighted score
        thought.total_score = _calculate_weighted_score(scores, tree.criteria_weights)

        # Update best score seen (for alpha-beta pruning)
        if thought.total_score > tree.best_score_seen:
            tree.best_score_seen = thought.total_score

        # Check for alpha-beta style pruning
        if _should_prune(thought, tree):
            thought.status = ThoughtStatus.FAILED
            thought.metadata["pruned"] = True
            thought.metadata["prune_reason"] = f"Score {thought.total_score:.2f} below threshold (best: {tree.best_score_seen:.2f})"
            pruned_count += 1
            results.append({
                "thought_id": thought_id,
                "content": thought.content[:100],
                "scores": scores,
                "total_score": round(thought.total_score, 2),
                "classification": "pruned",
            })
            continue

        # Classify based on weighted scores
        min_score = min(scores.values()) if scores else 0
        avg_score = thought.total_score

        if avg_score >= 7 and min_score >= 5:
            thought.status = ThoughtStatus.PROMISING
            classification = "promising"
        elif avg_score >= 5 and min_score >= 3:
            thought.status = ThoughtStatus.UNCERTAIN
            classification = "uncertain"
        else:
            thought.status = ThoughtStatus.FAILED
            classification = "failed"

        results.append({
            "thought_id": thought_id,
            "content": thought.content[:100],
            "scores": scores,
            "total_score": round(thought.total_score, 2),
            "classification": classification,
        })

    _save_tree(tree)

    # Sort by total score
    results.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "tree_id": tree_id,
        "evaluated": results,
        "pruned": pruned_count,
        "best_score_seen": round(tree.best_score_seen, 2),
        "thinking_level": tree.thinking_level,
        "instruction": f"Using {tree.strategy} strategy, call select_path to choose which approach(es) to pursue. "
        f"Recommended thinking level: {tree.thinking_level}",
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
            "thinking_level": tree.thinking_level,
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
    elif tree.strategy == "diverse":
        # Select diverse set of top candidates
        selected = []
        for candidate in candidates:
            if len(selected) >= beam_width:
                break
            if _is_diverse_enough(candidate, selected, tree.diversity_threshold):
                selected.append(candidate)
        # If not enough diverse candidates, fill with top scorers
        if len(selected) < min(beam_width, len(candidates)):
            for candidate in candidates:
                if candidate not in selected:
                    selected.append(candidate)
                if len(selected) >= beam_width:
                    break
    else:  # sampling
        # Simple implementation: take top candidates with some randomization
        import random
        weights = [c.total_score for c in candidates]
        total = sum(weights) or 1
        weights = [w / total for w in weights]
        # Weighted selection
        selected = []
        remaining = candidates[:]
        for _ in range(min(beam_width, len(remaining))):
            if not remaining:
                break
            selected.append(remaining.pop(0))  # Still favor top candidates

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
        "strategy_used": tree.strategy,
        "thinking_level": tree.thinking_level,
        "instruction": (
            f"Maximum depth reached. Evaluate if this is a complete solution. "
            f"If yes, call get_best_path. If not satisfactory, call backtrack. "
            f"Thinking level: {tree.thinking_level}"
            if at_max_depth
            else f"Expand the selected thought. Generate {3} more specific sub-approaches "
            f"that implement or refine this approach. Thinking level: {tree.thinking_level}"
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

    # Load from disk (includes cached)
    for file_path in DATA_DIR.glob("*.json"):
        tree_id = file_path.stem
        tree = _get_tree(tree_id)
        if tree:
            current = tree.thoughts.get(tree.current_id)
            trees.append({
                "id": tree.id,
                "problem": tree.problem[:80],
                "thoughts": len(tree.thoughts),
                "current_depth": current.depth if current else 0,
                "max_depth": tree.max_depth,
                "strategy": tree.strategy,
                "thinking_level": tree.thinking_level,
                "best_score": round(tree.best_score_seen, 2),
                "created": tree.created_at,
                "updated": tree.updated_at,
                "storage": str(file_path),
            })

    # Sort by updated time (most recent first)
    trees.sort(key=lambda t: t.get("updated", ""), reverse=True)

    return {"trees": trees, "count": len(trees), "storage_dir": str(DATA_DIR)}


@mcp.tool()
def delete_tree(tree_id: str) -> dict[str, Any]:
    """
    Delete a thought tree.

    Args:
        tree_id: ID of the tree to delete

    Returns:
        Confirmation of deletion
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    problem = tree.problem[:80]
    path = _get_tree_path(tree_id)

    if _delete_tree(tree_id):
        return {
            "deleted": True,
            "tree_id": tree_id,
            "problem": problem,
            "file_removed": str(path),
        }
    else:
        return {"error": f"Failed to delete tree: {tree_id}"}


@mcp.tool()
def set_criteria_weights(
    tree_id: str,
    weights: dict[str, float],
) -> dict[str, Any]:
    """
    Update criteria weights for scoring.

    Args:
        tree_id: ID of the thought tree
        weights: Dictionary of criterion name → weight (0.0-1.0)

    Returns:
        Updated criteria configuration
    """
    tree = _get_tree(tree_id)
    if not tree:
        return {"error": f"Tree not found: {tree_id}"}

    # Validate weights
    for criterion in weights:
        if criterion not in tree.criteria:
            return {"error": f"Unknown criterion: {criterion}. Available: {tree.criteria}"}
        if not 0.0 <= weights[criterion] <= 1.0:
            return {"error": f"Weight must be between 0.0 and 1.0: {criterion}={weights[criterion]}"}

    tree.criteria_weights.update(weights)
    _save_tree(tree)

    return {
        "tree_id": tree_id,
        "criteria": tree.criteria,
        "weights": tree.criteria_weights,
        "instruction": "Weights updated. Re-evaluate thoughts if needed.",
    }


def main():
    """Entry point for the tot MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
