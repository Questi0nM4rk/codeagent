# Future Ideas

Ideas that emerged during brainstorming but are not part of any current plan.

## Memory System

### SurrealML Embedded Inference

Run embedding models directly inside SurrealDB via ONNX. Eliminates OpenAI API dependency for embeddings. Would require exporting `text-embedding-3-small` equivalent to ONNX format, or using an open-source model like `all-MiniLM-L6-v2`.

**When**: After v1 is stable. Only if OpenAI costs become a concern.

### Memory Decay / Confidence Erosion

Memories lose confidence over time if not accessed. Useful for patterns that become outdated. Could implement via SurrealDB event on a cron schedule.

```surql
-- Hypothetical: decay confidence of unaccessed memories
UPDATE memory SET confidence *= 0.99
WHERE last_accessed < time::now() - 30d AND type = "pattern";
```

### Decision Memory Auto-Creation

When `/plan` runs, automatically create `type: "decision"` memories from the architect's tradeoff analysis. Links to the task that triggered the decision.

### Cross-Project Knowledge Transfer

When starting a new project, search all projects for transferable knowledge:
- Architecture patterns from similar projects
- Common pitfalls (episodes) from same tech stack
- Proven testing strategies

### Hook-Driven Passive Learning

Like claude-mem's approach: automatically capture observations from `PostToolUse` hooks without explicit `store` calls. Build session summaries at `SessionEnd`. Minimal agent effort for maximum knowledge capture.

### Live Query Monitoring Dashboard

Use SurrealDB live queries to stream failures and memory creation to a web dashboard:

```surql
LIVE SELECT * FROM memory WHERE type = "episode" AND metadata.outcome = "failure";
```

Real-time visibility into agent learning.

### Memory Consolidation

Periodically merge related knowledge memories into consolidated summaries. Like sleep consolidation in human memory. Reduces noise, strengthens core knowledge.

```
Before: 5 separate memories about "Python import patterns"
After: 1 consolidated memory with all insights, linking to originals
```

## Task System

### Parallel Execution Detection from Graph

Use SurrealDB graph traversal to detect which tasks can run in parallel based on `files_exclusive` overlap:

```surql
-- Find tasks with no file conflicts
SELECT * FROM task
WHERE status = "pending"
AND array::intersect(files_exclusive, $current_task.files_exclusive) = [];
```

### Task Dependency Auto-Resolution

When a blocking task completes, automatically unblock dependents:

```surql
DEFINE EVENT task_unblock ON TABLE task WHEN $event = "UPDATE"
    AND $after.status = "done" THEN (
    UPDATE task SET status = "pending"
    WHERE depends_on CONTAINS $after.id AND status = "blocked";
);
```

### Cost Tracking

Track token usage per task. Use `model_effectiveness` data to estimate cost before starting:

```python
# "This task pattern typically costs ~50k tokens with opus, ~15k with haiku"
```

## Infrastructure

### Embedded SurrealDB

Use `surrealkv://` storage backend instead of Docker container. Simpler deployment, no Docker dependency. Trade-off: no web UI, no multi-client access.

### Distributed Mode

When scaling to teams, switch from `surrealkv://` to `tikv://` for horizontal scaling. SurrealDB supports this natively.

### Memory Export/Import

Export memories as portable format (JSON-LD?) for sharing between developers or teams. Import curated knowledge bases for new projects.

## Search

### Ngram Index for Fuzzy Matching

Add edgengram analyzer for autocomplete-style search:

```surql
DEFINE ANALYZER fuzzy_analyzer
    TOKENIZERS blank
    FILTERS lowercase, edgengram(3, 10);
```

### Multi-Language Stemming

Snowball supports 17 languages. Could detect code comments language and apply appropriate stemmer.

### Context-Aware Search Boosting

Boost results from same project, same language, same recent session. Requires composing relevance signals beyond raw similarity.

## Agent System

### Memory-Informed Agent Selection

Use memory graph to determine which agent skill is most relevant. If a task is similar to past failures that a specific approach solved, suggest that approach.

### Automated Retrospectives

After completing an epic, automatically generate a retrospective by analyzing all episodes (failures + successes) associated with the epic's tasks. Store as a consolidated `pattern` memory.
