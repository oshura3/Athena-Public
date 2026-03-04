# PR: Add Ollama Embedding Support for Local-First Vector Storage

> **Type**: Feature Addition  
> **Scope**: Add Ollama as alternative embedding provider to Google Gemini  
> **Breaking Changes**: None (fully backward compatible)  
> **Related Issue**: Addresses gap in local-first deployment options — provides privacy-preserving alternative to cloud-based embeddings  
> **Status**: ✅ Implementation Complete | 🔄 Integration Tests Pending

---

## Summary

This PR adds support for **Ollama** as a local embedding provider, giving users a privacy-first, cost-free alternative to Google Gemini for generating vector embeddings stored in Supabase.

### Gap This Addresses
Athena currently requires internet connectivity and sends all data to Google for embedding generation. This prevents:
- Air-gapped/offline usage
- Privacy-sensitive deployments
- Zero-cost operation at scale

### What This Enables
- **Zero API costs** — Ollama runs locally, no cloud API calls
- **Privacy-first** — Data never leaves your machine during embedding
- **Offline capability** — Works without internet after initial setup
- **Drop-in replacement** — Switch via `EMBEDDING_PROVIDER` env var
- **Backward compatible** — Existing Gemini setups continue working unchanged

---

## Changes Made

### Core Implementation

| File | Change | Description |
|------|--------|-------------|
| `src/athena/memory/vectors.py` | ✅ Enhanced | Added `_get_embedding_ollama()` and provider routing logic; refactored `get_embedding()` to support provider selection |
| `examples/scripts/lib/shared_utils.py` | ✅ Enhanced | Added Ollama support to shared embedding utilities; preserved Gemini LRU caching |
| `.env.example` | ✅ Updated | Added `EMBEDDING_PROVIDER`, `OLLAMA_URL`, `OLLAMA_MODEL` configuration variables |

### Documentation

| File | Change | Description |
|------|--------|-------------|
| `docs/GUIDE_Supabase_with_Ollama_Embeddings.md` | ✅ New | Complete user-facing setup guide with 15 step-by-step instructions |
| `PR_ideas/TECHNICAL_IMPLEMENTATION_REPORT.md` | ✅ Reference | Detailed technical documentation for code reviewers |

---

## How It Works

### Provider Selection

```python
from athena.memory.vectors import get_embedding

# Auto-detects from EMBEDDING_PROVIDER env var
embedding = get_embedding("Your text here")

# Or explicitly specify
embedding = get_embedding("Your text here", provider="ollama")
```

### Environment Configuration

```bash
# Choose provider: "gemini" or "ollama"
EMBEDDING_PROVIDER=ollama

# Ollama settings (only needed if provider=ollama)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# Gemini settings (only needed if provider=gemini)
GOOGLE_API_KEY=your-api-key
```

---

## Testing Performed

### Unit Tests Completed ✅

| Test | Description | Result |
|------|-------------|--------|
| ✅ Ollama connection | Port 11434 responding | PASS |
| ✅ Embedding dimensions | 768 dimensions confirmed | PASS |
| ✅ Provider selection logic | EMBEDDING_PROVIDER env var works | PASS |
| ✅ Backward compatibility | Gemini still default | PASS |
| ✅ Persistent caching | Works with both providers | PASS |

### Integration Tests Pending 🔄

| Test | Description | Status |
|------|-------------|--------|
| ⬜ End-to-end sync to Supabase | Full sync with Ollama embeddings | PENDING |
| ⬜ Semantic search | Search functionality with Ollama vectors | PENDING |

### Test Commands for Reviewers

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Test embedding generation
python -c "
from athena.memory.vectors import get_embedding
emb = get_embedding('test', provider='ollama')
print(f'✅ {len(emb)} dimensions generated')
"
```

---

## Compatibility Matrix

| Feature | Gemini (Cloud) | Ollama (Local) | Notes |
|---------|----------------|----------------|-------|
| **Dimensions** | 768 or 3072 | 768 | Schema uses 768 — perfect match |
| **Requires Internet** | ✅ Yes | ❌ No | Ollama works offline |
| **API Cost** | Free tier | Free | Ollama is fully free |
| **Privacy** | Data sent to Google | 100% local | Data never leaves machine |
| **Setup Complexity** | Low | Medium | Ollama requires installation |
| **Caching** | ✅ Yes | ✅ Yes | Same cache works for both |

**Note**: Athena's Supabase schema uses `VECTOR(768)`, which matches Ollama's `nomic-embed-text` output perfectly. No schema migration required.

---

## Setup Instructions (for Testing)

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Windows
# Download from https://ollama.com/download

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama and Pull Model

```bash
# Start server
ollama serve

# In another terminal, pull embedding model
ollama pull nomic-embed-text
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env - set these values:
EMBEDDING_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text
```

### 4. Verify Installation

```bash
python -c "
from athena.memory.vectors import get_embedding
emb = get_embedding('test', provider='ollama')
print(f'✅ {len(emb)} dimensions generated')
"
```

---

## Migration Guide

### Existing Users (No Changes Required)

If you're already using Gemini:
```bash
# Your existing .env continues to work
GOOGLE_API_KEY=your-key
# EMBEDDING_PROVIDER defaults to "gemini"
```

### Switching to Ollama

```bash
# Edit .env
EMBEDDING_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# Install and start Ollama
ollama pull nomic-embed-text
ollama serve

# Done! No code changes needed
```

---

## Architecture Highlights

### Provider Selection Flow

```
User Request
      │
      ▼
get_embedding(text, provider=None)
      │
      ├── provider=None ──→ Read EMBEDDING_PROVIDER env var
      │                         (default: "gemini")
      │
      ├── provider="ollama" ──→ _get_embedding_ollama(text)
      │                              ├── Check cache first
      │                              ├── POST to Ollama API
      │                              ├── Cache result
      │                              └── Return 768-dim vector
      │
      └── provider="gemini" ──→ _get_embedding_gemini(text)
                                     ├── Check cache first
                                     ├── POST to Gemini API
                                     ├── Cache result
                                     └── Return 768-dim vector
```

### Key Design Decisions

1. **Backward Compatibility**: Default provider is "gemini" if not specified
2. **Unified Caching**: Same persistent cache works for both providers
3. **Error Handling**: Specific error messages for Ollama-specific issues
4. **Timeouts**: Longer timeout (120s vs 30s) for local CPU inference
5. **Text Truncation**: 8192 char limit prevents issues with large inputs

---

## Files to Review

1. **`src/athena/memory/vectors.py`** — Core embedding logic with dual provider support
2. **`examples/scripts/lib/shared_utils.py`** — Shared utilities for scripts
3. **`.env.example`** — Updated configuration template

---

## Checklist

- [x] Code follows project style guidelines
- [x] New functions have docstrings
- [x] Error messages are user-friendly
- [x] Environment variables documented
- [x] No breaking changes to existing API
- [x] Backward compatibility maintained
- [x] Unit tests completed (Ollama connection, dimensions, provider selection)
- [ ] Integration tests completed (pending final verification)

---

## Performance Comparison

| Metric | Ollama (Local) | Gemini (Cloud) |
|--------|---------------|----------------|
| **Latency** | 50-500ms* | 100-300ms |
| **Cost** | Free | Free tier available |
| **Privacy** | ✅ 100% local | ❌ Sent to Google |
| **Offline** | ✅ Works | ❌ Requires internet |
| **Setup** | Requires install | API key only |
| **Dimensions** | 768 | 768 or 3072 |

*Depends on hardware (GPU vs CPU)

---

## Security Considerations

### Ollama
- ✅ 100% local processing — no data leaves machine
- ✅ No API keys or authentication required
- ✅ Models run in isolated environment

### Supabase (Unchanged)
- Use **ANON key** in client applications
- Enable RLS policies for multi-user deployments
- Never commit `.env` to version control

---

## Related Documentation

- [Technical Implementation Report](TECHNICAL_IMPLEMENTATION_REPORT.md) — Detailed technical documentation
- [User Setup Guide](GUIDE_Supabase_with_Ollama_Embeddings.md) — Step-by-step user instructions
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai)
- [nomic-embed-text Model](https://ollama.com/library/nomic-embed-text)

---

## Why This Belongs in Athena

This PR directly addresses a **clear gap** in Athena's deployment options:

1. **Privacy is a core value** — Athena handles sensitive user data; local embeddings align with this
2. **Offline capability enables new use cases** — Air-gapped environments, travel, low-connectivity areas
3. **Cost-free at scale** — No API rate limits or pricing concerns for heavy users
4. **Zero friction adoption** — Existing users unaffected; new users can choose
5. **Proven pattern** — The author already uses this successfully with Kilo Code indexing

---

## Development History

This implementation was developed across focused sessions:

### Session 06: Infrastructure Setup (2026-03-03)
- Verified Ollama installation and model availability
- Confirmed 768-dimensional output compatibility
- Implemented core embedding functions

### Session 07: Integration & Documentation (2026-03-03)
- Added provider selection logic
- Updated shared utilities
- Created comprehensive documentation
- Prepared PR materials

---

*This PR was prepared following the [Contributing Guidelines](CONTRIBUTING.md). All changes are tested (unit tests complete) and documented. Integration tests pending final verification.*
