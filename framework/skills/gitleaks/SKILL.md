---
name: gitleaks
description: Secret detection via gitleaks and detect-secrets. Activates when dealing with leaked secrets, API keys, or credential management.
---

# Secret Detection Skill

Two tools run in pre-commit: **gitleaks** (primary) and **detect-secrets** (enhanced).

## Gitleaks

Scans commits for secrets (API keys, tokens, passwords, private keys).

Pre-commit hook: `gitleaks` v8.21.2

### What It Catches

- API keys (AWS, GCP, Azure, GitHub, Stripe, etc.)
- Private keys (RSA, SSH, PGP)
- JWT tokens
- Database connection strings with passwords
- Generic high-entropy strings that look like secrets

## Detect-secrets (Yelp)

Enhanced secret detection with baseline support.

Pre-commit hook: `detect-secrets --baseline .secrets.baseline`

The baseline file tracks known false positives so they don't re-trigger.

## Detect-private-key

Simple hook that catches committed private keys (`-----BEGIN.*PRIVATE KEY-----`).

## What to Do When Triggered

1. **Remove the secret from code immediately**
2. Move to environment variable or secrets manager
3. Reference via `os.environ["KEY_NAME"]` or `.env` file (gitignored)
4. If already committed: rotate the secret (it's in git history)

## .env Pattern

```bash
# .env (gitignored)
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
```

```python
import os
api_key = os.environ["OPENAI_API_KEY"]
```

## False Positives

Update the baseline:

```bash
detect-secrets scan --baseline .secrets.baseline
```

## Commands

```bash
# Scan for secrets
gitleaks detect --source .

# Scan specific commits
gitleaks detect --source . --log-opts "HEAD~5..HEAD"

# Update detect-secrets baseline
detect-secrets scan --baseline .secrets.baseline
```
