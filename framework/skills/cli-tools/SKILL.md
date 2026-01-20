---
name: cli-tools
description: CLI-first tool usage for code execution sandbox. Activates when interacting with external services (GitHub, AWS, Azure, Kubernetes). Guides when to use CLIs vs MCPs.
---

# CLI Tools Skill

Use command-line interfaces inside the code execution sandbox for external service interactions.

## The Iron Law

```
PREFER CLI OVER MCP WHEN THE CLI HAS JSON OUTPUT AND EXISTING AUTH
```

CLIs leverage your existing authentication (SSH keys, CLI login sessions) and provide full feature access.

## Decision Matrix

| Service   | Approach   | CLI   | Auth Method   | JSON Flag   |
| --------- | ---------- | ----- | ------------- | ----------- |
| GitHub | **CLI** | `gh` | `gh auth login` (SSH) | `--json` |
| AWS | **CLI** | `aws` | `~/.aws/credentials` | `--output json` |
| Azure | **CLI** | `az` | `az login` | `--output json` |
| Kubernetes | **CLI** | `kubectl` | `~/.kube/config` | `-o json` |
| Docker | **CLI** | `docker` | socket | `--format json` |
| Jira/Confluence | **MCP** | - | API token | Structured response |
| Memory/Context | **MCP** | - | - | Letta for persistence |
| Large MCP results | **Sandbox** | - | - | Filter in code-execution |

## When to Use CLI

- Service has good CLI with JSON output
- You have existing auth configured (SSH, CLI login, credentials file)
- Need full feature access beyond MCP subset
- Simple command execution, not document search

## When to Use MCP

- Need to search/filter large document sets (Confluence, docs)
- No good CLI exists
- Need persistent state/memory (Letta)

## When to Use code-execution with servers=[]

For large MCP results that would bloat context:

```python
# servers=["letta"] loads letta MCP inside sandbox
mcp__code-execution__run_python(
    code='''
passages = mcp_letta.list_passages(search="auth")
relevant = [p for p in passages if "JWT" in p.text][:5]
print(f"Found {len(relevant)} relevant: {[p.text[:50] for p in relevant]}")
''',
    servers=["letta"]
)
# Returns ~200 tokens instead of full passage list
```

Use this pattern when:
- MCP results could be large (many passages, symbols, etc.)
- Need to filter/transform before returning to context
- Want to combine multiple MCP calls efficiently

## CLI Usage Patterns

### GitHub (gh)

### Good Example: GitHub API
```python
import subprocess
import json

# List issues with JSON output
result = subprocess.run(
    ['gh', 'issue', 'list', '--repo', 'owner/repo', '--json', 'number,title,state'],
    capture_output=True, text=True
)
issues = json.loads(result.stdout)

# Filter in sandbox - only summary returns to context
open_bugs = [i for i in issues if 'bug' in i.get('labels', [])]
print(f"Found {len(open_bugs)} open bugs")
```
Uses existing auth, filters in sandbox, minimal context return

### Bad Example
```python
# DON'T: Using GitHub MCP without code execution
issues = await mcp_github.list_issues(owner="x", repo="y")
# Full response goes to context - token bloat
```
Full response bloats context, requires separate API token

### AWS (aws)

### Good Example: AWS S3
```python
import subprocess
import json

# List S3 buckets
result = subprocess.run(
    ['aws', 's3api', 'list-buckets', '--output', 'json'],
    capture_output=True, text=True
)
buckets = json.loads(result.stdout)['Buckets']

# Process in sandbox
for bucket in buckets:
    print(f"{bucket['Name']}: {bucket['CreationDate']}")
```
Uses ~/.aws/credentials automatically

### Kubernetes (kubectl)

### Good Example: Kubernetes Pods
```python
import subprocess
import json

# Get pods
result = subprocess.run(
    ['kubectl', 'get', 'pods', '-n', 'production', '-o', 'json'],
    capture_output=True, text=True
)
pods = json.loads(result.stdout)['items']

# Filter unhealthy
unhealthy = [p for p in pods if p['status']['phase'] != 'Running']
```
Uses ~/.kube/config automatically

### Azure (az)

### Good Example: Azure Resource Groups
```python
import subprocess
import json

# List resource groups
result = subprocess.run(
    ['az', 'group', 'list', '--output', 'json'],
    capture_output=True, text=True
)
groups = json.loads(result.stdout)
```
Uses az login session

## Common Rationalizations

| Excuse   | Reality   |
| -------- | --------- |
| "MCP is more structured" | CLI with `--json` gives same structure |
| "Need to set up auth" | CLIs use existing auth you already have |
| "MCP is easier" | CLI in sandbox = one subprocess call |
| "I don't know CLI flags" | Use `gh --help`, `aws help`, etc. |

## Red Flags - Use MCP Instead

- Need fuzzy search across documents
- Managing persistent memory/context (Letta)
- No JSON output available from CLI
- CLI requires interactive input
- Results are small enough that filtering isn't needed

## Verification Checklist

Before using CLI in sandbox:
- [ ] CLI is installed (check with `which <cli>`)
- [ ] Auth is configured (run auth status command)
- [ ] JSON output flag is available
- [ ] Command doesn't require interactive input

## Auth Status Commands

```bash
# GitHub
gh auth status

# AWS
aws sts get-caller-identity

# Azure
az account show

# Kubernetes
kubectl cluster-info
```

## When Stuck

| Problem   | Solution   |
| --------- | ---------- |
| Auth not working | Run CLI auth command outside sandbox first |
| No JSON output | Check CLI docs for `--format` or `-o` flags |
| Missing CLI | Add to codeagent tools install |
| Interactive required | Fall back to MCP or API calls |
