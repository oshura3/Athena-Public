"""
athena.memory.vectors — Thread-Safe v1.2

Optimizations:
    - Thread-Local Clients: Prevents httpx connection state corruption in parallel loops.
    - Atomic Cache: PersistentEmbeddingCache now uses Locks and Atomic Writes.
"""

import os
import sys
import hashlib
import json
import threading
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

# Global cache instance
_embedding_cache = None
_embedding_cache_lock = threading.Lock()


def get_embedding_cache():
    global _embedding_cache
    with _embedding_cache_lock:
        if _embedding_cache is None:
            _embedding_cache = PersistentEmbeddingCache()
        return _embedding_cache


# Thread-local storage for Supabase clients
_thread_local = threading.local()


def get_client() -> Any:
    """Returns a thread-safe Supabase client instance."""
    if not hasattr(_thread_local, "client"):
        from supabase import create_client
        from dotenv import load_dotenv

        load_dotenv()

        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in environment.")
        _thread_local.client = create_client(url, key)
    return _thread_local.client


class PersistentEmbeddingCache:
    """JSON-backed persistent cache with Thread-Safe Atomic Writes and Background Saving."""

    def __init__(self, filename="embedding_cache.json"):
        # Correct pathing via project discovery
        from athena.core.config import AGENT_DIR

        self.cache_file = AGENT_DIR / "state" / filename
        self.lock = threading.Lock()
        self._cache: Dict[str, List[float]] = {}
        self._dirty = False
        self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                with self.lock:
                    self._cache = json.loads(self.cache_file.read_text())
            except Exception:
                self._cache = {}

    def _save_worker(self, content: str):
        """Worker thread for atomic disk operations."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            # Atomic swap pattern
            fd, temp_path = tempfile.mkstemp(dir=self.cache_file.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(temp_path, self.cache_file)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception:
            pass

    def _save(self):
        """Schedules a background atomic save."""
        try:
            with self.lock:
                if not self._dirty:
                    return
                content = json.dumps(self._cache)
                self._dirty = False

            # Offload IO to a daemon thread to avoid blocking caller
            threading.Thread(
                target=self._save_worker, args=(content,), daemon=True
            ).start()
        except Exception:
            pass

    def get(self, text_hash: str) -> Optional[List[float]]:
        with self.lock:
            return self._cache.get(text_hash)

    def set(self, text_hash: str, embedding: List[float]):
        with self.lock:
            self._cache[text_hash] = embedding
            self._dirty = True
        self._save()


def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def get_embedding(text: str, provider: str = None) -> List[float]:
    """Generate embedding with persistent disk caching.

    Supports both Google Gemini (cloud) and Ollama (local) providers.
    
    Args:
        text: The text to embed
        provider: "gemini", "ollama", or None (auto-detect from env)
        
    Returns:
        List of floats representing the embedding vector
    """
    # Check cache first (regardless of provider)
    text_hash = _hash_text(text)
    cache = get_embedding_cache()
    cached = cache.get(text_hash)
    if cached:
        return cached
    
    # Auto-detect provider from environment
    if provider is None:
        provider = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    
    # Route to appropriate implementation
    if provider == "ollama":
        embedding = _get_embedding_ollama(text)
    elif provider == "gemini":
        embedding = _get_embedding_gemini(text)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}. Use 'gemini' or 'ollama'.")
    
    # Cache and return
    cache.set(text_hash, embedding)
    return embedding


def _get_embedding_gemini(text: str) -> List[float]:
    """Generate embedding using Google Gemini API.
    
    Uses gemini-embedding-001 (768 or 3072 dimensions depending on task_type).
    """
    import requests
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing. Set it in your .env file or switch to Ollama provider.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["embedding"]["values"]


def _get_embedding_ollama(text: str) -> List[float]:
    """Generate embedding using local Ollama instance.
    
    Supports any Ollama embedding model (nomic-embed-text, mxbai-embed-large, etc.)
    Defaults to 768-dimensional embeddings compatible with Athena's schema.
    
    Requires:
        - Ollama running on localhost:11434 (or OLLAMA_URL env var)
        - Model pulled and available (default: nomic-embed-text)
        
    Raises:
        ConnectionError: If Ollama is not running
        ValueError: If model is not found
    """
    import requests
    
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
    
    # Ollama embeddings endpoint
    try:
        response = requests.post(
            f"{url}/api/embeddings",
            json={
                "model": model,
                "prompt": text[:8192]  # Truncate if needed (model dependent)
            },
            timeout=120  # Local models can be slow on CPU
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot connect to Ollama at {url}. "
            "Make sure Ollama is running (ollama serve or Ollama app)."
        )
    
    if response.status_code == 404:
        raise ValueError(
            f"Model '{model}' not found in Ollama. "
            f"Run: ollama pull {model}"
        )
    
    response.raise_for_status()
    return response.json()["embedding"]


def search_rpc(
    rpc_name: str, query_embedding: List[float], limit: int = 5, threshold: float = 0.3
) -> List[Dict]:
    client = get_client()
    result = client.rpc(
        rpc_name,
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


# --- Collection-Specific Wrappers ---


def search_sessions(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_sessions", query_embedding, limit, threshold)


def search_case_studies(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_case_studies", query_embedding, limit, threshold)


def search_protocols(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_protocols", query_embedding, limit, threshold)


def search_capabilities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_capabilities", query_embedding, limit, threshold)


def search_playbooks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_playbooks", query_embedding, limit, threshold)


def search_references(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_references", query_embedding, limit, threshold)


def search_frameworks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_frameworks", query_embedding, limit, threshold)


def search_workflows(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_workflows", query_embedding, limit, threshold)


def search_entities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_entities", query_embedding, limit, threshold)


def search_user_profile(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_user_profile", query_embedding, limit, threshold)


def search_system_docs(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_system_docs", query_embedding, limit, threshold)


def search_insights(client, query_embedding, limit=5, threshold=0.3):
    """Search insights table (Marketing Analysis, Strategic Notes)."""
    return search_rpc("search_insights", query_embedding, limit, threshold)
