from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).with_name("demo_docs.json")


@lru_cache(maxsize=1)
def load_documents() -> tuple[dict[str, object], ...]:
    raw_documents = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return tuple(raw_documents)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def search_documents(query: str, limit: int = 5) -> list[dict[str, str]]:
    tokens = _tokenize(query)
    if not tokens:
        return []

    scored_results: list[tuple[int, dict[str, object]]] = []
    for document in load_documents():
        title_tokens = set(_tokenize(str(document["title"])))
        tag_tokens = set(_tokenize(" ".join(document.get("tags", []))))
        body_tokens = _tokenize(str(document["text"]))

        score = 0
        for token in tokens:
            if token in title_tokens:
                score += 5
            if token in tag_tokens:
                score += 3
            score += body_tokens.count(token)

        if score:
            scored_results.append((score, document))

    scored_results.sort(
        key=lambda item: (-item[0], str(item[1]["title"]).lower(), str(item[1]["id"]).lower())
    )

    return [
        {
            "id": str(document["id"]),
            "title": str(document["title"]),
            "url": str(document["url"]),
        }
        for _, document in scored_results[:limit]
    ]


def fetch_document(document_id: str) -> dict[str, object]:
    for document in load_documents():
        if document["id"] == document_id:
            return {
                "id": str(document["id"]),
                "title": str(document["title"]),
                "text": str(document["text"]),
                "url": str(document["url"]),
                "metadata": {
                    "category": str(document["category"]),
                    "updated_at": str(document["updated_at"]),
                    "tags": list(document.get("tags", [])),
                },
            }

    raise KeyError(f"Unknown document id: {document_id}")

