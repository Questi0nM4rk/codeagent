---
name: supabase
description: Supabase development expertise. Activates when discussing Supabase auth, database, storage, edge functions, or real-time subscriptions.
---

# Supabase Development Skill

Domain knowledge for Supabase backend development with security-first approach.

## The Iron Law

```
RLS ON EVERY TABLE + TYPED CLIENT + LOCAL-FIRST DEVELOPMENT
Every table has Row Level Security. TypeScript types generated from schema. Test locally before push.
```

## Core Principle

> "Your database is your API. RLS policies are your authorization layer. Never trust the client."

## Stack

| Component | Technology |
|-----------|------------|
| Database | PostgreSQL with pgvector, PostGIS |
| Auth | Supabase Auth (GoTrue) |
| Storage | S3-compatible object storage |
| Functions | Deno Edge Functions |
| Real-time | PostgreSQL LISTEN/NOTIFY |

## When to Use

**Always:**
- Building apps with Supabase backend
- Setting up authentication flows
- Writing database migrations
- Creating Edge Functions
- Configuring storage policies

**Exceptions (ask human partner):**
- Complex multi-tenant architectures (may need custom auth)
- High-frequency writes exceeding Supabase limits

## Workflow

### Step 1: Local Setup

```bash
supabase init
supabase start
```

### Step 2: Schema + RLS

Create migrations with RLS policies from the start.

### Step 3: Generate Types

```bash
supabase gen types typescript --local > src/types/supabase.ts
```

### Step 4: Test Locally

Test all auth flows and queries against local instance.

### Step 5: Push to Remote

```bash
supabase link --project-ref <project-id>
supabase db push --linked
```

## CLI Commands

```bash
# Initialize project
supabase init

# Start local development
supabase start
supabase stop

# Database
supabase db reset
supabase db push
supabase db pull
supabase db diff --file migration_name

# Migrations
supabase migration new migration_name
supabase migration list
supabase migration up
supabase migration down

# Edge Functions
supabase functions new function_name
supabase functions serve
supabase functions deploy function_name

# Generate types
supabase gen types typescript --local > src/types/supabase.ts

# Link to remote
supabase link --project-ref <project-id>
supabase db push --linked
```

## Examples

### Client Setup

<Good>
```typescript
import { createClient } from '@supabase/supabase-js';
import type { Database } from './types/supabase';

// Client-side: anon key only
const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

// Server-side: service role, no session persistence
const supabaseAdmin = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { persistSession: false } }
);
```
- Typed client with generated `Database` type
- Anon key for client, service role for server only
- Session persistence disabled for admin client
</Good>

<Bad>
```typescript
const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // DANGER!
);
```
- No type safety
- Service role key exposed to client
- Bypasses all RLS policies
</Bad>

### Row Level Security

<Good>
```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read published posts
CREATE POLICY "Public posts are visible to everyone"
ON posts FOR SELECT
USING (published = true);

-- Policy: Users can only update their own posts
CREATE POLICY "Users can update own posts"
ON posts FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can insert their own posts
CREATE POLICY "Users can insert own posts"
ON posts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own posts
CREATE POLICY "Users can delete own posts"
ON posts FOR DELETE
USING (auth.uid() = user_id);
```
- RLS enabled before any policies
- Separate policies for each operation (SELECT, INSERT, UPDATE, DELETE)
- Uses `auth.uid()` for user identification
- `WITH CHECK` for write operations
</Good>

<Bad>
```sql
-- No RLS, table is public!
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT
);

-- Or worse: RLS enabled but no policies
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
-- Forgot to create policies - table now inaccessible!
```
- Missing RLS exposes all data
- RLS without policies blocks all access
- No `auth.uid()` validation
</Bad>

### Database Queries

<Good>
```typescript
// Select with filters and joins
const { data, error } = await supabase
  .from('posts')
  .select('id, title, author:users(name)')
  .eq('published', true)
  .order('created_at', { ascending: false })
  .limit(10);

if (error) throw error;

// Insert with returning
const { data, error } = await supabase
  .from('posts')
  .insert({ title: 'Hello', content: 'World' })
  .select()
  .single();
```
- Uses typed client for autocomplete
- Handles errors explicitly
- Uses `.select()` to get inserted data
- `.single()` for single row operations
</Good>

### Real-time Subscriptions

<Good>
```typescript
// Subscribe to table changes
const channel = supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'posts',
      filter: 'user_id=eq.' + userId,
    },
    (payload) => {
      console.log('Change:', payload);
    }
  )
  .subscribe();

// Cleanup on unmount
return () => {
  supabase.removeChannel(channel);
};
```
- Named channel for identification
- Filtered by user for security
- Proper cleanup to prevent memory leaks
</Good>

<Bad>
```typescript
// Subscribing to all changes without filter
supabase
  .channel('all-posts')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'posts' }, handler)
  .subscribe();
// Never cleaned up - memory leak!
```
- No filter exposes all changes
- Missing cleanup causes memory leaks
</Bad>

### Edge Functions

<Good>
```typescript
// supabase/functions/hello/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  // Create client with user's auth context
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    {
      global: {
        headers: { Authorization: req.headers.get('Authorization')! },
      },
    }
  );

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return new Response('Unauthorized', { status: 401 });
  }

  return new Response(
    JSON.stringify({ message: 'Hello', user: user.email }),
    { headers: { 'Content-Type': 'application/json' } }
  );
});
```
- Uses anon key, not service role
- Inherits user's auth context from request
- Validates user before proceeding
- Proper error response for unauthorized
</Good>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll add RLS later" | Data is exposed now. Add RLS first. |
| "It's just a prototype" | Prototypes become production. Secure from day one. |
| "Service role is easier" | It bypasses security. Use only server-side. |
| "Types slow me down" | Types catch bugs. Generate them from schema. |
| "Local testing is slow" | It's faster than debugging production issues. |

## Red Flags - STOP and Start Over

These indicate security issues:

- Table without `ENABLE ROW LEVEL SECURITY`
- Service role key in client-side code
- RLS enabled but no policies defined
- Hardcoded credentials in code
- Missing `auth.uid()` checks in policies
- Edge Function using service role without validation
- No type generation from schema

If you see these, stop and fix security first.

## Verification Checklist

Before considering the task complete:

- [ ] All tables have RLS enabled
- [ ] Each table has policies for SELECT, INSERT, UPDATE, DELETE as needed
- [ ] TypeScript types generated from schema
- [ ] Service role key only used server-side
- [ ] Edge Functions validate authentication
- [ ] Storage buckets have appropriate policies
- [ ] Tested against local Supabase instance
- [ ] Migrations checked into version control

## Review Tools

```bash
# Type generation
supabase gen types typescript --local > types.ts

# Diff migrations
supabase db diff

# Lint SQL
sqlfluff lint supabase/migrations/ --dialect postgres

# Check local status
supabase status
```

## When Stuck

| Problem | Solution |
|---------|----------|
| RLS blocking all queries | Check policies exist and use correct `auth.uid()` |
| Types out of sync | Regenerate with `supabase gen types typescript --local` |
| Migration conflicts | `supabase db reset` locally, then `supabase db pull` |
| Auth not working locally | Check `supabase status` for auth service URL |
| Real-time not receiving | Verify RLS allows SELECT for the filter conditions |
| Edge Function timeout | Check for blocking operations, use async properly |

## Related Skills

- `typescript` - For type-safe client usage
- `python` - For Edge Functions alternative (Deno)
- `reviewer` - Uses sqlfluff for SQL validation
- `tdd` - Test against local Supabase before push
