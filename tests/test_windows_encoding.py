"""Tests for Windows console Unicode encoding compatibility."""
import pytest
from io import StringIO
import sys


class TestSafePrint:
    """Test suite for safe_print utility."""
    
    def test_safe_print_import(self):
        """Verify safe_print can be imported."""
        from athena.utils.safe_print import safe_print
        assert callable(safe_print)
    
    def test_safe_print_unicode_support(self):
        """Verify safe_print works with Unicode."""
        from athena.utils.safe_print import safe_print
        # Should not raise an exception
        safe_print("🧠 Test message with emoji")
    
    def test_safe_print_fallback(self):
        """Verify safe_print fallback mapping."""
        from athena.utils.safe_print import get_emoji_fallback
        emoji_map = get_emoji_fallback()
        
        # Check key emojis are mapped
        assert "🧠" in emoji_map
        assert emoji_map["🧠"] == "[ATHENA]"
        assert "✅" in emoji_map
        assert emoji_map["✅"] == "[OK]"
        assert "⚠️" in emoji_map
        assert emoji_map["⚠️"] == "[WARNING]"
        assert "❌" in emoji_map
        assert emoji_map["❌"] == "[ERROR]"
    
    def test_emoji_mapping_completeness(self):
        """Verify emoji mapping covers common CLI emojis."""
        from athena.utils.safe_print import get_emoji_fallback
        emoji_map = get_emoji_fallback()
        
        # Core emojis used in CLI
        required_emojis = [
            "🩺", "✅", "⚠️", "❌", "🔑", "📚", "📦", "🚀",
            "🛑", "💾", "⚙️", "🔍", "🧠", "🌐", "💻", "📊",
            "⏱️", "✨", "🔄", "📝", "🎯", "🏗️", "🧪"
        ]
        
        for emoji in required_emojis:
            assert emoji in emoji_map, f"Missing emoji: {emoji}"


class TestSupportsUnicode:
    """Test suite for Unicode support detection."""
    
    def test_supports_unicode_import(self):
        """Verify supports_unicode can be imported."""
        from athena.utils.safe_print import supports_unicode
        assert callable(supports_unicode)
    
    def test_supports_unicode_returns_bool(self):
        """Verify supports_unicode returns a boolean."""
        from athena.utils.safe_print import supports_unicode
        result = supports_unicode()
        assert isinstance(result, bool)
