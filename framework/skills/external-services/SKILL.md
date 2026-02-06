---
name: external-services
description: MCP-first external service integration via code-execution sandbox. Activates when interacting with external services (GitHub, AWS, Azure, Kubernetes). Uses MCPs when available, CLIs as fallback.
---

# External Services Skill

Use MCPs inside the code-execution sandbox for external service interactions. This provides filtered results with minimal context usage.

## The Iron Law

```bash
PREFER MCP OVER CLI WHEN AN MCP EXISTS FOR THE SERVICE
```

MCPs loaded via `servers=[]` in code-execution provide structured responses and consistent auth patterns.

## Decision Matrix

| Service    | Approach | Package/CLI                            | Auth                     |
|:-----------|:---------|:---------------------------------------|:-------------------------|
| GitHub     | **MCP**  | `@modelcontextprotocol/server-github`  | `GITHUB_TOKEN`           |
| A-MEM      | **MCP**  | `amem-mcp`                             | `OPENAI_API_KEY`         |
| Tavily     | **MCP**  | `tavily-mcp`                           | `TAVILY_API_KEY`         |
| Figma      | **MCP**  | `figma-developer-mcp`                  | `FIGMA_API_KEY`          |
| Supabase   | **MCP**  | `@supabase/mcp-server-supabase`        | `SUPABASE_ACCESS_TOKEN`  |
| AWS        | **CLI**  | `aws`                                  | `~/.aws/credentials`     |
| Azure      | **CLI**  | `az`                                   | `az login`               |
| Kubernetes | **CLI**  | `kubectl`                              | `~/.kube/config`         |

## When to Use MCP (Preferred)

- Service has an MCP package available
- Need structured API responses
- Want consistent auth via API tokens
- No CLI installation required in sandbox

## When to Use CLI (Fallback)

- No good MCP exists for the service
- Need offline/cached access
- Need full CLI feature access beyond MCP subset
- Already have CLI auth configured locally

## MCP Usage Pattern

Load MCPs inside code-execution with `servers=[]`:

### GitHub (MCP)

```python
mcp__code-execution__run_python(
    code='''
issues = mcp_github.list_issues(owner="owner", repo="repo")
open_bugs = [i for i in issues if "bug" in i.get("labels", [])][:10]
print(f"Found {len(open_bugs)} open bugs")
for bug in open_bugs:
    print(f"- #{bug['number']}: {bug['title']}")
''',
    servers=["github"]
)
```

### A-MEM (MCP)

```python
mcp__code-execution__run_python(
    code='''
memories = mcp_amem.search_memory(query="authentication", k=5)
relevant = [m for m in memories if "JWT" in m.content]
print(f"Found {len(relevant)} relevant memories")
for m in relevant:
    print(f"- {m.content[:100]}...")
''',
    servers=["amem"]
)
```

### Tavily (MCP)

```python
mcp__code-execution__run_python(
    code='''
results = mcp_tavily.search("Python async best practices 2025")
for r in results[:3]:
    print(f"- {r['title']}: {r['url']}")
''',
    servers=["tavily"]
)
```

## CLI Fallback Pattern

For services without MCPs, use subprocess:

### AWS (CLI)

```python
mcp__code-execution__run_python(
    code='''
import subprocess, json

result = subprocess.run(
    ['aws', 's3api', 'list-buckets', '--output', 'json'],
    capture_output=True, text=True
)
buckets = json.loads(result.stdout)['Buckets']
print(f"Found {len(buckets)} buckets")
for b in buckets[:5]:
    print(f"- {b['Name']}")
'''
)
```

### Kubernetes (CLI)

```python
mcp__code-execution__run_python(
    code='''
import subprocess, json

result = subprocess.run(
    ['kubectl', 'get', 'pods', '-n', 'production', '-o', 'json'],
    capture_output=True, text=True
)
pods = json.loads(result.stdout)['items']
unhealthy = [p for p in pods if p['status']['phase'] != 'Running']
print(f"Unhealthy pods: {len(unhealthy)}")
for p in unhealthy:
    print(f"- {p['metadata']['name']}: {p['status']['phase']}")
'''
)
```

### Azure (CLI)

```python
mcp__code-execution__run_python(
    code='''
import subprocess, json

result = subprocess.run(
    ['az', 'group', 'list', '--output', 'json'],
    capture_output=True, text=True
)
groups = json.loads(result.stdout)
print(f"Found {len(groups)} resource groups")
'''
)
```

## Common Rationalizations

| Excuse | Reality |
| :----- | :------ |
| "CLI is simpler" | MCP via servers=[] is one parameter |
| "Need CLI features" | MCPs cover most common operations |
| "Already have CLI auth" | API tokens are more portable |
| "MCP responses are big" | That's why we filter in code-execution |

## Red Flags - Use CLI Instead

- No MCP exists for the service
- Need offline/cached data access
- MCP doesn't support required operation
- CLI has better error messages for debugging

## Auth Status Commands

For CLI fallback, verify auth:

```bash
# AWS
aws sts get-caller-identity

# Azure
az account show

# Kubernetes
kubectl cluster-info
```

## When Stuck

| Problem | Solution |
| :------ | :------- |
| MCP not loading | Check `servers=[]` parameter spelling |
| Auth failing | Verify env key is set in .env |
| CLI not found | Service needs CLI fallback pattern |
| Results too large | Add filtering in Python before print |
