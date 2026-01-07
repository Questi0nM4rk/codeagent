---
name: supabase
description: Supabase development expertise. Activates when discussing Supabase auth, database, storage, edge functions, or real-time subscriptions.
---

# Supabase Development Skill

Domain knowledge for Supabase backend development.

## Stack

- **Database**: PostgreSQL with pgvector, PostGIS
- **Auth**: Supabase Auth (GoTrue)
- **Storage**: S3-compatible object storage
- **Functions**: Deno Edge Functions
- **Real-time**: PostgreSQL LISTEN/NOTIFY

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

## Patterns

### Client Setup (TypeScript)

```typescript
import { createClient } from '@supabase/supabase-js';
import type { Database } from './types/supabase';

const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

// Server-side with service role
const supabaseAdmin = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { persistSession: false } }
);
```

### Authentication

```typescript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password',
});

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password',
});

// OAuth
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: { redirectTo: 'http://localhost:3000/auth/callback' },
});

// Get session
const { data: { session } } = await supabase.auth.getSession();

// Sign out
await supabase.auth.signOut();

// Auth state listener
supabase.auth.onAuthStateChange((event, session) => {
  console.log(event, session);
});
```

### Database Queries

```typescript
// Select with filters
const { data, error } = await supabase
  .from('posts')
  .select('id, title, author:users(name)')
  .eq('published', true)
  .order('created_at', { ascending: false })
  .limit(10);

// Insert
const { data, error } = await supabase
  .from('posts')
  .insert({ title: 'Hello', content: 'World' })
  .select()
  .single();

// Update
const { data, error } = await supabase
  .from('posts')
  .update({ title: 'Updated' })
  .eq('id', postId)
  .select()
  .single();

// Upsert
const { data, error } = await supabase
  .from('posts')
  .upsert({ id: postId, title: 'Upserted' })
  .select();

// Delete
const { error } = await supabase
  .from('posts')
  .delete()
  .eq('id', postId);

// RPC (stored function)
const { data, error } = await supabase
  .rpc('get_user_stats', { user_id: userId });
```

### Row Level Security (RLS)

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

-- Service role bypass (for admin operations)
-- Use supabaseAdmin client with service_role key
```

### Storage

```typescript
// Upload file
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${userId}/avatar.png`, file, {
    cacheControl: '3600',
    upsert: true,
  });

// Download file
const { data, error } = await supabase.storage
  .from('avatars')
  .download('path/to/file.png');

// Get public URL
const { data } = supabase.storage
  .from('avatars')
  .getPublicUrl('path/to/file.png');

// Create signed URL
const { data, error } = await supabase.storage
  .from('private')
  .createSignedUrl('path/to/file.png', 60); // 60 seconds

// Delete file
const { error } = await supabase.storage
  .from('avatars')
  .remove(['path/to/file.png']);
```

### Real-time Subscriptions

```typescript
// Subscribe to table changes
const channel = supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    {
      event: '*', // INSERT, UPDATE, DELETE
      schema: 'public',
      table: 'posts',
      filter: 'user_id=eq.' + userId,
    },
    (payload) => {
      console.log('Change:', payload);
    }
  )
  .subscribe();

// Broadcast (ephemeral messages)
const channel = supabase.channel('room-1');
channel
  .on('broadcast', { event: 'cursor' }, (payload) => {
    console.log('Cursor:', payload);
  })
  .subscribe();

channel.send({
  type: 'broadcast',
  event: 'cursor',
  payload: { x: 100, y: 200 },
});

// Cleanup
supabase.removeChannel(channel);
```

### Edge Functions

```typescript
// supabase/functions/hello/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
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

  return new Response(
    JSON.stringify({ message: 'Hello', user: user?.email }),
    { headers: { 'Content-Type': 'application/json' } }
  );
});
```

## Testing Patterns

```typescript
// Use local Supabase for tests
const supabase = createClient(
  'http://localhost:54321',
  'eyJ...' // local anon key from supabase start
);

// Reset database between tests
beforeEach(async () => {
  await supabase.rpc('truncate_tables');
});
```

## Review Tools

```bash
# Type generation
supabase gen types typescript --local > types.ts

# Diff migrations
supabase db diff

# Lint SQL
sqlfluff lint supabase/migrations/ --dialect postgres
```

## Common Conventions

- Enable RLS on all tables
- Use `auth.uid()` in policies
- Generate TypeScript types from schema
- Use migrations for schema changes
- Use Edge Functions for server-side logic
- Store files in buckets with appropriate policies
- Use `service_role` key only server-side
