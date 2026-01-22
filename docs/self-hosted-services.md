# Self-Hosted Services Documentation

CodeAgent uses three self-hosted open-source services as alternatives to cloud-only tools.

---

## Quick Reference

| Service | Replaces | URL | Docs |
|---------|----------|-----|------|
| **Penpot** | Figma | http://localhost:9001 | [help.penpot.app](https://help.penpot.app/technical-guide/) |
| **Appwrite** | Supabase/Firebase | http://localhost:8585 | [appwrite.io/docs](https://appwrite.io/docs/advanced/self-hosting) |
| **Convex** | Supabase (realtime) | http://localhost:3210 | [docs.convex.dev](https://docs.convex.dev/self-hosting) |

---

## 1. Penpot (Design Platform)

### What It Is
Open-source design and prototyping platform. Full Figma alternative with collaborative features.

### Official Docs
- **Installation**: https://help.penpot.app/technical-guide/getting-started/docker/
- **Configuration**: https://help.penpot.app/technical-guide/configuration/
- **GitHub**: https://github.com/penpot/penpot

### Architecture
```
┌─────────────────┐     ┌─────────────────┐
│  penpot-frontend│────▶│  penpot-backend │
│    (nginx)      │     │    (clojure)    │
│    :9001        │     └────────┬────────┘
└─────────────────┘              │
                                 ▼
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼─────┐           ┌───────▼───────┐
              │ PostgreSQL│           │    Valkey     │
              │   :5432   │           │  (Redis-like) │
              └───────────┘           └───────────────┘
```

### Services (6 containers)
| Container | Purpose | Port |
|-----------|---------|------|
| penpot-frontend | Web UI (nginx) | 9001 |
| penpot-backend | API server (Clojure) | internal |
| penpot-exporter | PDF/SVG export | internal |
| penpot-postgres | Database | internal |
| penpot-valkey | WebSocket cache | internal |
| penpot-mailcatch | Dev email testing | 1080 |

### CodeAgent Setup
We use a simplified docker-compose at `infrastructure/services/penpot.yml` that:
- Disables email verification (dev mode)
- Enables password login and registration
- Uses local filesystem for assets
- Exposes mail UI at :1080 for testing

### Manual Official Setup
```bash
# Download official compose
curl -o docker-compose.yaml https://raw.githubusercontent.com/penpot/penpot/main/docker/images/docker-compose.yaml

# Start with specific version
PENPOT_VERSION=2.4.3 docker compose -p penpot -f docker-compose.yaml up -d

# Create admin user
docker exec -ti penpot-penpot-backend-1 python3 manage.py create-profile
```

### API Access
Penpot has a REST API but no official MCP. Interact via:
- Browser at http://localhost:9001
- REST API (undocumented, reverse-engineer from network tab)
- PREPL server for admin commands

---

## 2. Appwrite (Backend-as-a-Service)

### What It Is
Full BaaS with authentication, database, storage, and serverless functions. Supabase/Firebase alternative.

### Official Docs
- **Installation**: https://appwrite.io/docs/advanced/self-hosting/installation
- **Configuration**: https://appwrite.io/docs/advanced/self-hosting
- **GitHub**: https://github.com/appwrite/appwrite

### System Requirements
| Resource | Minimum |
|----------|---------|
| CPU | 2 cores |
| RAM | 4 GB |
| Swap | 2 GB |
| Docker Compose | v2+ |

### The "Complicated" Installer

Appwrite uses an **interactive installer** that generates a custom docker-compose.yml:

```bash
# Official installer (interactive)
docker run -it --rm \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume "$(pwd)"/appwrite:/usr/src/code/appwrite:rw \
    --entrypoint="install" \
    appwrite/appwrite:1.8.1
```

**What the installer prompts for:**
1. HTTP port (default: 80)
2. HTTPS port (default: 443)
3. Secret encryption key
4. Main hostname
5. DNS A record hostname

**What it generates:**
- `appwrite/docker-compose.yml` - Full production config (~25+ services)
- `appwrite/.env` - Environment configuration

### Full Appwrite Architecture (Production)
```
                    ┌─────────────┐
                    │   Traefik   │ (reverse proxy)
                    │   :80/:443  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌─────▼─────┐
   │ Console │       │    API    │      │ Realtime  │
   │  (Web)  │       │  (Main)   │      │ (WebSocket│
   └─────────┘       └─────┬─────┘      └───────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
┌────▼────┐          ┌─────▼─────┐         ┌────▼────┐
│ MariaDB │          │   Redis   │         │ Workers │
│         │          │           │         │ (many)  │
└─────────┘          └───────────┘         └─────────┘
```

### Production Services (~25 containers)
- **Core**: appwrite, appwrite-realtime, appwrite-console
- **Database**: mariadb
- **Cache**: redis
- **Workers**: audits, webhooks, deletes, databases, builds, certificates, functions, mails, messaging, migrations
- **Tasks**: maintenance, stats-resources, scheduler-functions, scheduler-executions, scheduler-messages
- **Runtime**: openruntimes-executor, openruntimes-proxy
- **Dev tools**: maildev, coredns

### CodeAgent Setup (Simplified)
Our `infrastructure/services/appwrite.yml` is a **minimal dev setup**:
- Single appwrite container
- MariaDB + Redis
- No workers, no functions runtime
- Port 8585 (to avoid conflicts)

**For full features**, run the official installer:
```bash
cd ~/.codeagent/infrastructure/services
docker run -it --rm \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume "$(pwd)"/appwrite-full:/usr/src/code/appwrite:rw \
    --entrypoint="install" \
    appwrite/appwrite:1.8.1
```

### API Access
```bash
# REST API
curl http://localhost:8585/v1/health

# SDKs available for:
# - JavaScript/TypeScript
# - Python
# - PHP
# - Ruby
# - Dart/Flutter
# - Swift
# - Kotlin
```

---

## 3. Convex (Reactive Backend)

### What It Is
TypeScript-first reactive backend with real-time sync. Think "Firebase Realtime Database meets Supabase".

### Official Docs
- **Self-hosting guide**: https://github.com/get-convex/convex-backend/blob/main/self-hosted/README.md
- **Main docs**: https://docs.convex.dev/self-hosting
- **GitHub**: https://github.com/get-convex/convex-backend

### Architecture (Simple)
```
┌─────────────────┐     ┌─────────────────┐
│    Dashboard    │────▶│     Backend     │
│     :6791       │     │     :3210       │
└─────────────────┘     │     :3211       │ (HTTP actions)
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │  SQLite/Postgres│
                        │   (internal)    │
                        └────────────────┘
```

### Services (2 containers)
| Container | Purpose | Port |
|-----------|---------|------|
| convex-backend | API + database | 3210, 3211 |
| convex-dashboard | Web UI | 6791 |

### Setup Steps

```bash
# 1. Start services
docker compose -f infrastructure/services/convex.yml up -d

# 2. Generate admin key
docker compose exec convex-backend ./generate_admin_key.sh

# 3. In your project, create .env.local
echo 'CONVEX_SELF_HOSTED_URL=http://127.0.0.1:3210' >> .env.local
echo 'CONVEX_SELF_HOSTED_ADMIN_KEY=<your-key>' >> .env.local

# 4. Push code to your backend
npx convex dev
```

### Key Difference from Cloud
Instead of `CONVEX_DEPLOY_KEY`, use:
- `CONVEX_SELF_HOSTED_URL` - Your backend URL
- `CONVEX_SELF_HOSTED_ADMIN_KEY` - Generated admin key

### Database Options
| Option | Config |
|--------|--------|
| SQLite (default) | Built-in, stored in Docker volume |
| PostgreSQL | Set `POSTGRES_URL` env var |
| MySQL | Set `MYSQL_URL` env var |

### API Access
```typescript
// In your app
import { ConvexClient } from "convex/browser";

const client = new ConvexClient("http://localhost:3210");
```

---

## Comparison: When to Use What

| Need | Service |
|------|---------|
| **Design mockups/prototypes** | Penpot |
| **User auth + database** | Appwrite |
| **Real-time sync + TypeScript** | Convex |
| **Full BaaS with functions** | Appwrite (full install) |
| **Simple reactive queries** | Convex |

### Resource Usage

| Service | RAM | CPU | Containers |
|---------|-----|-----|------------|
| Penpot | ~1-2 GB | Low | 6 |
| Appwrite (minimal) | ~1 GB | Low | 3 |
| Appwrite (full) | ~4+ GB | Medium | 25+ |
| Convex | ~512 MB | Low | 2 |

---

## CodeAgent Integration

### Current State
All services run via Docker Compose but have **no MCPs yet**.

### Interacting with Services

**Option 1: code-execution MCP**
```python
# Via code-execution sandbox
import requests
response = requests.get("http://host.docker.internal:8585/v1/health")
```

**Option 2: Direct CLI**
```bash
# Convex CLI
npx convex dev --url http://localhost:3210

# Appwrite CLI
npx appwrite client --endpoint http://localhost:8585/v1
```

**Option 3: Future MCPs**
We can write simple MCPs that wrap:
- Penpot: REST API for projects/files
- Appwrite: REST/GraphQL for all services
- Convex: TypeScript SDK for queries/mutations

---

## Troubleshooting

### Services Not Starting
```bash
# Check Docker network exists
docker network ls | grep codeagent-network

# Create if missing
docker network create codeagent-network

# Check individual service logs
docker logs codeagent-penpot-backend
docker logs codeagent-convex-backend
docker logs codeagent-appwrite
```

### Port Conflicts
| Service | Default | CodeAgent |
|---------|---------|-----------|
| Penpot | 9001 | 9001 |
| Appwrite | 80/443 | 8585 |
| Convex | 3210 | 3210 |

### Reset Everything
```bash
# Stop all services
docker compose -f ~/.codeagent/infrastructure/services/penpot.yml down -v
docker compose -f ~/.codeagent/infrastructure/services/convex.yml down -v
docker compose -f ~/.codeagent/infrastructure/services/appwrite.yml down -v

# Remove volumes (WARNING: deletes all data)
docker volume rm $(docker volume ls -q | grep codeagent_ || true)
```

---

## References

### Penpot
- Docs: https://help.penpot.app/technical-guide/
- GitHub: https://github.com/penpot/penpot
- Community: https://community.penpot.app/

### Appwrite
- Docs: https://appwrite.io/docs
- GitHub: https://github.com/appwrite/appwrite
- Discord: https://discord.gg/appwrite

### Convex
- Docs: https://docs.convex.dev/
- GitHub: https://github.com/get-convex/convex-backend
- Discord: https://discord.gg/convex (#self-hosted channel)
