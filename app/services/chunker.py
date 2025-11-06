"""Custom text chunker used instead of LangChain's splitters.

Provides a simple, sentence-aware character-based chunker with overlap.
Two strategies are supported:
 - "small": chunk_size=300, overlap=50
 - default/"recursive": chunk_size=800, overlap=100

The splitter attempts to break on sentence boundaries (., !, ? and newlines)
preferentially; if no boundary is available within the window it falls back to a
hard split at the chunk_size. Overlap is applied between chunks.

This module has no external dependencies and is safe to use for preparing
documents before embedding.
"""
from __future__ import annotations

import re
from typing import List


SentenceBoundaryRegex = re.compile(r'[\.!?]["\']?\s+|\n+')


def _find_last_boundary(text: str, start: int, end: int) -> int | None:
	"""Return the index (end position) of the last sentence boundary within
	text[start:end]. If none found, return None.
	"""
	# Search for boundaries using finditer and keep last end <= end
	last: int | None = None
	for m in SentenceBoundaryRegex.finditer(text, start, end):
		last = m.end()
	return last


def chunk_text(text: str, strategy: str = "recursive") -> List[str]:
	"""Chunk `text` according to the selected strategy.

	Args:
		text: Full text to chunk.
		strategy: "small" for smaller chunks, anything else for default.

	Returns:
		A list of text chunks (strings). Chunks are stripped of leading/trailing
		whitespace but otherwise preserve original content.
	"""
	if not text:
		return []

	text = text.strip()
	if strategy == "small":
		chunk_size = 300
		overlap = 50
	else:
		chunk_size = 800
		overlap = 100

	n = len(text)
	if n <= chunk_size:
		return [text]

	chunks: List[str] = []
	start = 0
	# Minimal forward advance to avoid infinite loops
	min_advance = max(1, chunk_size // 10)

	while start < n:
		end = min(start + chunk_size, n)

		if end == n:
			chunk = text[start:n].strip()
			if chunk:
				chunks.append(chunk)
			break

		# Prefer to split at the last sentence boundary before `end`.
		split_pos = _find_last_boundary(text, start, end)

		# If boundary is too close to start (creating tiny chunk) or not found,
		# fall back to a hard split at `end`.
		if split_pos is None or split_pos - start <= overlap:
			split_pos = end

		chunk = text[start:split_pos].strip()
		if chunk:
			chunks.append(chunk)

		# Compute next start position applying overlap. Ensure progress.
		next_start = max(split_pos - overlap, start + min_advance)
		if next_start <= start:
			# Failsafe: move forward at least min_advance
			next_start = start + min_advance

		start = next_start

	return chunks


def _demo_small_test() -> None:
	"""Small self-test when run as a script. Not a replacement for unit tests,
	just a quick sanity check used during development.
	"""
	sample = (
		"This is a first sentence. Here is a second sentence that is a bit "
		"longer and intended to test splitting.\n\nNow a new paragraph to see "
		"how the chunker handles blank lines. Finally a concluding sentence!"
	)
	print("Original length:", len(sample))
	for name in ("small", "recursive"):
		ch = chunk_text(sample, strategy=name)
		print(f"Strategy={name} -> {len(ch)} chunks")
		for i, c in enumerate(ch, 1):
			print(f"--- chunk {i} (len={len(c)}) ---\n{c}\n")


if __name__ == "__main__":
	_demo_small_test()

