import unittest

from catalog import fetch_document, search_documents


class CatalogTests(unittest.TestCase):
    def test_search_prefers_pricing_for_billing_queries(self) -> None:
        results = search_documents("pricing seats billing")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "pricing")

    def test_search_respects_limit(self) -> None:
        results = search_documents("workspace product support reporting", limit=2)
        self.assertLessEqual(len(results), 2)

    def test_fetch_returns_metadata(self) -> None:
        document = fetch_document("security")
        self.assertEqual(document["metadata"]["category"], "policy")
        self.assertIn("encrypts", document["text"])

    def test_fetch_unknown_document_raises(self) -> None:
        with self.assertRaises(KeyError):
            fetch_document("missing-doc")


if __name__ == "__main__":
    unittest.main()

