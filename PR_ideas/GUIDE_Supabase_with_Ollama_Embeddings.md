# Supabase Setup with Ollama Embeddings — Complete Guide

> **Purpose**: Set up cloud-based vector storage (Supabase) using local embeddings (Ollama) for privacy-first semantic search  
> **Time Required**: ~30-45 minutes  
> **Difficulty**: Beginner (step-by-step instructions provided)  
> **Last Updated**: 2026-03-03

---

## What This Setup Enables

| Feature | Benefit |
|---------|---------|
| **Cloud Vector Storage** | Your embeddings stored securely in Supabase, accessible from any device |
| **Local Embedding Generation** | Text converted to vectors using Ollama (100% offline, zero API costs) |
| **Semantic Search** | Find related content by meaning, not just keywords |
| **Privacy-First** | Sensitive data never leaves your machine during embedding |

---

## Quick Overview: How It Works

```
Your Documents
      │
      ▼ (locally, offline)
┌─────────────────┐
│  Ollama Server  │ ← Runs on your machine
│  (Embedding AI) │   Converts text → 768-dimension vectors
└────────┬────────┘
         │
         ▼ (encrypted HTTPS)
┌─────────────────┐
│    Supabase     │ ← Cloud PostgreSQL with pgvector
│  (Vector Store) │   Stores vectors + metadata
└─────────────────┘
         │
         ▼ (query results)
   Semantic Search
   (find similar content)
```

---

## Prerequisites

- [ ] GitHub account (for Supabase sign-up)
- [ ] Windows 11 with PowerShell (or macOS/Linux with Terminal)
- [ ] Python 3.10+ installed
- [ ] Internet connection (for initial setup only)

---

## Part 1: Supabase Setup (Cloud Storage)

### Step 1: Create Supabase Account

1. Visit [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with **GitHub** (recommended) or email
4. Verify your email

### Step 2: Create New Project

1. Click **"New project"** in the dashboard
2. Configure:
   - **Project name**: `athena` (or your preference)
   - **Database password**: Save this securely (you'll need it for direct DB access)
   - **Region**: Choose closest to your location
3. Click **"Create project"**
4. Wait ~2 minutes for provisioning

### Step 3: Configure Security Settings

During setup, you'll see security options:

| Setting | Value | Why |
|---------|-------|-----|
| **Enable Data API** | ✅ YES | Required for Athena to connect |
| **Enable Automatic RLS** | ❌ NO (for personal use) | Skip if only you use it; simplifies setup |

> **Note**: You can enable RLS later if you share your workspace. For solo use, skip it.

### Step 4: Get Your Credentials

1. Go to your project dashboard
2. Click **Settings** (gear icon) → **API**
3. Copy these values (you'll need them in Step 6):
   - **Project URL** (e.g., `https://abc123.supabase.co`)
   - **anon public** key (NOT the service_role key!)

⚠️ **CRITICAL**: Use the **anon key** or **publishable key**, NOT the service_role key. The service_role key bypasses all security.

### Step 5: Enable pgvector Extension

1. In Supabase dashboard, go to **Database** → **Extensions**
2. Search for **"vector"** or **"pgvector"**
3. Click to expand options
4. For **Schema**, select **"public"**
5. Toggle to **Enable**

This enables vector similarity search in your database.

### Step 6: Run Database Schema

1. Go to **SQL Editor** (left sidebar)
2. Click **New query**
3. Open [`src/athena/memory/schema.sql`](../../src/athena/memory/schema.sql)
4. Copy entire contents
5. Paste into SQL Editor
6. Click **Run**

**What this creates:**
- `sessions` table — stores daily interaction logs
- `case_studies` table — pattern analysis documents
- `protocols` table — reusable thinking patterns
- IVFFlat indexes for fast similarity search
- RPC functions for semantic search

---

## Part 2: Ollama Setup (Local Embeddings)

### Step 7: Install Ollama

**Windows (PowerShell):**
```powershell
# Download from https://ollama.com/download
# Then verify installation:
ollama --version
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 8: Start Ollama Server

**Terminal 1:**
```powershell
# Start the server (keep this running)
ollama serve
```

Or use the desktop app (macOS/Windows) which starts automatically.

### Step 9: Pull Embedding Model

**Terminal 2** (new window):
```powershell
# Recommended: nomic-embed-text (768 dimensions, fast, accurate)
ollama pull nomic-embed-text

# Alternative: mxbai-embed-large (higher quality, slower)
# ollama pull mxbai-embed-large
```

Download time: 5-15 minutes depending on your connection.

### Step 10: Verify Ollama Works

```powershell
# Test embedding generation
curl http://localhost:11434/api/embeddings `
  -H "Content-Type: application/json" `
  -d '{"model": "nomic-embed-text", "prompt": "Hello world"}'
```

Expected output: JSON with a 768-number array.

---

## Part 3: Athena Configuration

### Step 11: Configure Environment Variables

1. **Copy the example .env file:**
   ```powershell
   # Check if .env exists
   Test-Path .env
   
   # If FALSE, copy from example
   Copy-Item .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```env
   # ================================================
   # Supabase Credentials (from Step 4)
   # ================================================
   SUPABASE_URL=https://your-actual-project.supabase.co
   SUPABASE_ANON_KEY=your-actual-anon-key-here
   
   # ================================================
   # Embedding Provider: "ollama" or "gemini"
   # ================================================
   EMBEDDING_PROVIDER=ollama
   
   # Ollama settings (only needed if provider=ollama)
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=nomic-embed-text
   
   # Gemini settings (only needed if provider=gemini)
   # GOOGLE_API_KEY=your-gemini-api-key
   ```

### Step 12: Verify Supabase Connection

```powershell
cd examples/scripts
python supabase_setup.py
```

Expected output:
```
============================================================
SUPABASE SCHEMA SETUP
============================================================
✅ Connected to: https://your-project.supabase.co

2️⃣  Checking if tables exist...
   ✅ 'sessions' table exists
   ✅ 'case_studies' table exists
   ✅ 'protocols' table exists
```

### Step 13: Test Embedding Generation

```powershell
# Quick Python test
python -c "
from athena.memory.vectors import get_embedding
emb = get_embedding('test', provider='ollama')
print(f'✅ {len(emb)} dimensions generated successfully')
"
```

Expected: `✅ 768 dimensions generated successfully`

---

## Part 4: Sync Your Data

### Step 14: Initial Sync (All Content)

```powershell
cd examples/scripts
python supabase_sync.py --all
```

This will:
- Chunk your Markdown files
- Generate embeddings using Ollama (locally)
- Upload vectors + metadata to Supabase

**Time required**: Depends on your data size. First sync may take 10-30 minutes.

### Step 15: Test Semantic Search

```powershell
cd examples/scripts
python supabase_search.py "recent work on API design"
```

If you get relevant results, everything is working! 🎉

---

## Troubleshooting

### Ollama Connection Error
```
ConnectionError: Cannot connect to Ollama at http://localhost:11434
```
**Solution:**
```powershell
# Ensure Ollama is running
ollama serve

# Check if port is available
netstat -ano | findstr :11434
```

### Model Not Found Error
```
ValueError: Model 'nomic-embed-text' not found in Ollama
```
**Solution:**
```powershell
# Pull the model
ollama pull nomic-embed-text

# List available models
ollama list
```

### Supabase Connection Error
```
ValueError: Supabase credentials missing in environment
```
**Solution:**
- Verify `.env` file exists in project root
- Check that `SUPABASE_URL` includes `https://`
- Ensure you're using the **anon key**, not service_role key
- Restart your terminal/IDE to reload environment

### "Table does not exist" Error
**Solution:**
- Re-run the schema.sql in Supabase SQL Editor (Step 6)
- Ensure pgvector extension is enabled (Step 5)

### "No results from search"
**Solution:**
- Run `supabase_sync.py --all` first to upload content
- Check that Ollama is running before syncing

---

## Provider Comparison

| Feature | Ollama (Local) | Gemini (Cloud) |
|---------|----------------|----------------|
| **Cost** | Free | Free tier available |
| **Privacy** | ✅ 100% local | ❌ Sent to Google |
| **Offline** | ✅ Works | ❌ Requires internet |
| **Latency** | 50-500ms* | 100-300ms |
| **Setup** | Medium (install + model) | Low (API key only) |
| **Dimensions** | 768 | 768 or 3072 |

*Depends on hardware (GPU vs CPU)

---

## Security Best Practices

### Supabase
- ✅ Use **ANON key** in `.env` (not service_role key)
- ✅ Never commit `.env` to git (it's in `.gitignore`)
- ✅ Enable RLS if sharing workspace with others
- ✅ Review diffs before pushing to ensure no API keys leak

### Ollama
- ✅ 100% local processing — no data leaves your machine
- ✅ No API keys required
- ✅ Models run in isolated environment

---

## Daily Usage Commands

| Task | Command |
|------|---------|
| Sync new content | `python supabase_sync.py --all` |
| Search vectors | `python supabase_search.py "your query"` |
| Optimize indexes | `python reindex_supabase.py` |
| Verify setup | `python supabase_setup.py` |

---

## Architecture Overview

### Provider Selection Flow

```
User Request
      │
      ▼
get_embedding(text, provider=None)
      │
      ├── provider=None ──→ Read EMBEDDING_PROVIDER env var
      │                         (defaults to "gemini")
      │
      ├── provider="ollama" ──→ POST to Ollama (localhost:11434)
      │                              └── Returns 768-dim vector
      │
      └── provider="gemini" ──→ POST to Gemini API
                                     └── Returns 768/3072-dim vector
```

### Caching

Both providers use persistent disk caching:
- **Location**: `.agent/state/embedding_cache.json`
- **Format**: MD5 hash → embedding vector
- **Benefit**: Avoids re-generating embeddings for identical text

---

## Switching Between Providers

### From Gemini to Ollama

```bash
# 1. Edit .env
EMBEDDING_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# 2. Install and start Ollama
ollama pull nomic-embed-text
ollama serve

# 3. Done! No code changes needed
```

### From Ollama to Gemini

```bash
# 1. Edit .env
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=your-api-key

# 2. Done! Gemini is the default
```

---

## Next Steps

1. **Read VECTORRAG.md** for advanced semantic search patterns
2. **Set up periodic sync** — Add `supabase_sync.py --all` to your workflow
3. **Explore the code** — Check `src/athena/memory/vectors.py` for implementation details

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [`docs/VECTORRAG.md`](VECTORRAG.md) | Full vector system documentation |
| [`docs/SEMANTIC_SEARCH.md`](SEMANTIC_SEARCH.md) | Search mechanics deep dive |
| [`src/athena/memory/schema.sql`](../src/athena/memory/schema.sql) | Database schema definition |
| [Ollama Docs](https://github.com/ollama/ollama/blob/main/docs/README.md) | Ollama official documentation |
| [Supabase Vector Guide](https://supabase.com/docs/guides/ai) | Supabase AI/vector docs |

---

*Document created for Athena workspace. For updates, check the latest schema.sql and related scripts.*
