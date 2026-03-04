#!/usr/bin/env python3
"""
shared_utils.py - Centralized logic for Athena scripts.
Reduces redundancy across searching, logging, and telemetry.
"""

import os
import sys
import hashlib
import requests
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv
from supabase import create_client, Client

# --- PATH RESOLUTION ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SDK_PATH = PROJECT_ROOT / "src"


def setup_paths():
    """Ensure SDK is in sys.path."""
    if str(SDK_PATH) not in sys.path:
        sys.path.insert(0, str(SDK_PATH))


# --- ENVIRONMENT & CLIENTS ---
def load_athena_env():
    """Load .env from project root."""
    load_dotenv(PROJECT_ROOT / ".env")
    return {
        "SUPABASE_URL": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    }


@lru_cache(None)
def get_supabase_client():
    """Singleton Supabase client."""
    env = load_athena_env()
    if not env["SUPABASE_URL"] or not env["SUPABASE_KEY"]:
        raise ValueError("Missing Supabase credentials in .env")
    return create_client(env["SUPABASE_URL"], env["SUPABASE_KEY"])


# --- AI & EMBEDDINGS ---
@lru_cache(maxsize=128)
def _get_embedding_cached_gemini(text_hash: str, text: str, api_key: str) -> tuple:
    """Internal cached embedding function for Gemini."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text}]},
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return tuple(response.json()["embedding"]["values"])


def _get_embedding_ollama(text: str, model: str = "nomic-embed-text") -> list:
    """Ollama embedding (no caching here - handled by vectors.py when imported)."""
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    try:
        response = requests.post(
            f"{url}/api/embeddings",
            json={"model": model, "prompt": text[:8192]},
            timeout=120
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


def get_embedding(text: str, provider: str = None):
    """Unified embedding with provider selection.
    
    Args:
        text: Text to embed
        provider: "gemini", "ollama", or None (auto-detect from EMBEDDING_PROVIDER env var)
        
    Returns:
        List of floats representing the embedding vector
    """
    if provider is None:
        provider = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    
    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
        return _get_embedding_ollama(text, model)
    else:
        # Default to Gemini
        env = load_athena_env()
        text_hash = hashlib.md5(text.encode()).hexdigest()
        result = _get_embedding_cached_gemini(text_hash, text, env["GOOGLE_API_KEY"])
        return list(result)


# --- COMPLIANCE ---
def log_violation(violation_type: str, message: str):
    """Log protocol compliance issues."""
    try:
        from athena.core.config import SCRIPTS_DIR
        import subprocess

        subprocess.run(
            [
                "python3",
                str(PROJECT_ROOT / ".agent" / "scripts" / "protocol_compliance.py"),
                "log",
                violation_type,
                message,
            ],
            capture_output=True,
        )
    except Exception:
        pass
