"""Unit tests for app/utils/text.py — clean_text() and chunk_text()."""

import pytest

from app.utils.text import clean_text, chunk_text


# ---------------------------------------------------------------------------
# clean_text()
# ---------------------------------------------------------------------------

class TestCleanText:
    def test_null_bytes_replaced(self):
        assert clean_text("hello\x00world") == "hello world"
        assert clean_text("a\u0000b") == "a b"
        assert clean_text("\x00\x00\x00") == ""

    def test_excessive_whitespace_compressed(self):
        assert clean_text("hello   world") == "hello world"
        assert clean_text("a\t\tb") == "a b"
        assert clean_text("a\n\n\nb") == "a b"
        assert clean_text("a \t \n b") == "a b"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_already_clean(self):
        assert clean_text("hello world") == "hello world"
        assert clean_text("one two three") == "one two three"

    def test_leading_trailing_whitespace_stripped(self):
        assert clean_text("  hello  ") == "hello"
        assert clean_text("\thello\n") == "hello"

    def test_null_bytes_and_whitespace_combined(self):
        assert clean_text("  \x00hello\x00  world  \x00  ") == "hello world"


# ---------------------------------------------------------------------------
# chunk_text()
# ---------------------------------------------------------------------------

class TestChunkText:
    def test_empty_string(self):
        assert chunk_text("") == []

    def test_whitespace_only(self):
        assert chunk_text("   ") == []
        assert chunk_text("\t\n ") == []

    def test_shorter_than_chunk_size(self):
        result = chunk_text("short", chunk_size=100, overlap=10)
        assert result == ["short"]

    def test_exactly_chunk_size(self):
        text = "a" * 50
        result = chunk_text(text, chunk_size=50, overlap=10)
        assert result == [text]

    def test_overlap_correctness(self):
        text = "a" * 100
        chunks = chunk_text(text, chunk_size=30, overlap=10)
        assert len(chunks) > 1
        for i in range(len(chunks) - 1):
            tail = chunks[i][-10:]
            head = chunks[i + 1][:10]
            assert tail == head, (
                f"Overlap mismatch between chunk {i} and {i+1}: "
                f"{tail!r} != {head!r}"
            )

    def test_unicode_cjk_and_emoji(self):
        cjk = "\u4e16\u754c" * 20  # 40 CJK characters
        chunks = chunk_text(cjk, chunk_size=15, overlap=5)
        assert len(chunks) > 1
        rejoined = chunks[0]
        for c in chunks[1:]:
            rejoined += c[5:]  # skip overlap portion
        assert rejoined == cjk

        emoji = "\U0001f600" * 30  # 30 emoji characters
        chunks = chunk_text(emoji, chunk_size=10, overlap=3)
        assert len(chunks) > 1

    def test_exact_boundaries_chunk10_overlap3(self):
        text = "abcdefghijklmnopqrstuvwxyz"  # 26 chars
        chunks = chunk_text(text, chunk_size=10, overlap=3)
        # chunk 0: start=0,  end=10, text[0:10]  = "abcdefghij"
        # chunk 1: start=7,  end=17, text[7:17]  = "hijklmnopq"
        # chunk 2: start=14, end=24, text[14:24] = "opqrstuvwx"
        # chunk 3: start=21, end=26, text[21:26] = "vwxyz"
        assert chunks == [
            "abcdefghij",
            "hijklmnopq",
            "opqrstuvwx",
            "vwxyz",
        ]

    def test_all_text_covered(self):
        text = "0123456789abcdef"  # 16 chars
        chunks = chunk_text(text, chunk_size=8, overlap=2)
        # Verify every character in text appears in at least one chunk
        covered = set()
        start = 0
        for chunk in chunks:
            idx = text.find(chunk, start)
            assert idx >= 0
            for j in range(idx, idx + len(chunk)):
                covered.add(j)
            start = idx
        assert covered == set(range(len(text)))
