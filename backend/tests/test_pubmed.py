"""Tests for PubMed-related functions in app.ingest."""

from unittest.mock import patch, MagicMock

import pytest

from app.ingest import (
    _abstract_to_text,
    _safe_get_year,
    build_pubmed_term,
    fetch_pubmed_docs,
    ingest_text_items,
)


# ---------------------------------------------------------------------------
# _abstract_to_text
# ---------------------------------------------------------------------------

class TestAbstractToText:
    def test_string_input_returned_unchanged(self):
        assert _abstract_to_text("hello world") == "hello world"

    def test_list_of_strings_joined_with_spaces(self):
        assert _abstract_to_text(["part one", "part two"]) == "part one part two"

    def test_list_of_dicts_with_label_and_text(self):
        objs = [
            {"Label": "Methods", "text": "We did X."},
            {"Label": "Results", "text": "We found Y."},
        ]
        result = _abstract_to_text(objs)
        assert "Methods: We did X." in result
        assert "Results: We found Y." in result

    def test_list_of_dicts_with_hash_text_key(self):
        objs = [{"Label": "Background", "#text": "Some background."}]
        result = _abstract_to_text(objs)
        assert "Background: Some background." in result

    def test_empty_input_returns_empty_string(self):
        assert _abstract_to_text(None) == ""
        assert _abstract_to_text("") == ""
        assert _abstract_to_text([]) == ""

    def test_mixed_list_strings_and_dicts(self):
        items = [
            "Plain text part.",
            {"Label": "Conclusion", "text": "We conclude Z."},
        ]
        result = _abstract_to_text(items)
        assert "Plain text part." in result
        assert "Conclusion: We conclude Z." in result

    def test_dict_without_label(self):
        objs = [{"text": "No label here."}]
        result = _abstract_to_text(objs)
        assert "No label here." in result
        # Should not have a label prefix
        assert result.strip() == "No label here."

    def test_non_standard_input_falls_back_to_str(self):
        result = _abstract_to_text(12345)
        assert result == "12345"


# ---------------------------------------------------------------------------
# _safe_get_year
# ---------------------------------------------------------------------------

class TestSafeGetYear:
    def test_article_date_with_year(self):
        article = {"ArticleDate": [{"Year": "2021"}]}
        assert _safe_get_year(article) == 2021

    def test_journal_pubdate_with_year(self):
        article = {
            "Journal": {
                "JournalIssue": {
                    "PubDate": {"Year": "2020"}
                }
            }
        }
        assert _safe_get_year(article) == 2020

    def test_medline_date(self):
        article = {
            "Journal": {
                "JournalIssue": {
                    "PubDate": {"MedlineDate": "2019 Jan-Feb"}
                }
            }
        }
        assert _safe_get_year(article) == 2019

    def test_missing_all_date_fields_returns_none(self):
        assert _safe_get_year({}) is None

    def test_invalid_year_format_returns_none(self):
        article = {
            "Journal": {
                "JournalIssue": {
                    "PubDate": {"MedlineDate": "not-a-year"}
                }
            }
        }
        assert _safe_get_year(article) is None

    def test_article_date_preferred_over_journal(self):
        article = {
            "ArticleDate": [{"Year": "2023"}],
            "Journal": {
                "JournalIssue": {
                    "PubDate": {"Year": "2022"}
                }
            },
        }
        assert _safe_get_year(article) == 2023

    def test_empty_article_date_list_falls_through(self):
        article = {
            "ArticleDate": [],
            "Journal": {
                "JournalIssue": {
                    "PubDate": {"Year": "2018"}
                }
            },
        }
        assert _safe_get_year(article) == 2018


# ---------------------------------------------------------------------------
# build_pubmed_term
# ---------------------------------------------------------------------------

class TestBuildPubmedTerm:
    def test_basic_query_no_filters(self):
        assert build_pubmed_term("diabetes", None, None, None, None) == "diabetes"

    def test_with_language_filter(self):
        result = build_pubmed_term("diabetes", "en", None, None, None)
        assert result == "diabetes AND English[lang]"

    def test_with_filter_types(self):
        result = build_pubmed_term("diabetes", None, ["Guideline", "Review"], None, None)
        assert result == "diabetes AND (Guideline[Publication Type] OR Review[Publication Type])"

    def test_with_language_and_types(self):
        result = build_pubmed_term("diabetes", "en", ["Review"], None, None)
        assert "AND English[lang]" in result
        assert "AND (Review[Publication Type])" in result

    def test_language_mapping(self):
        result = build_pubmed_term("test", "es", None, None, None)
        assert "Spanish[lang]" in result

    def test_unknown_language_passes_through(self):
        result = build_pubmed_term("test", "Klingon", None, None, None)
        assert "Klingon[lang]" in result

    def test_query_whitespace_stripped(self):
        result = build_pubmed_term("  diabetes  ", None, None, None, None)
        assert result == "diabetes"


# ---------------------------------------------------------------------------
# fetch_pubmed_docs (mocked Entrez)
# ---------------------------------------------------------------------------

def _make_fake_article(pmid, title, abstract_text, journal="Test Journal", year="2023"):
    """Build a fake PubmedArticle structure mimicking Entrez.read() output."""
    return {
        "MedlineCitation": {
            "PMID": pmid,
            "Article": {
                "ArticleTitle": title,
                "Abstract": {"AbstractText": abstract_text},
                "Journal": {
                    "Title": journal,
                    "JournalIssue": {
                        "PubDate": {"Year": year},
                    },
                },
                "ArticleDate": [{"Year": year}],
            },
        },
    }


class TestFetchPubmedDocs:
    @patch("app.ingest._entrez_fetch")
    @patch("app.ingest._entrez_search")
    @patch("app.ingest.time.sleep")
    def test_basic_fetch(self, mock_sleep, mock_search, mock_fetch):
        mock_search.return_value = {"IdList": ["123", "456"]}
        mock_fetch.return_value = {
            "PubmedArticle": [
                _make_fake_article("123", "Article One", "Abstract one text."),
                _make_fake_article("456", "Article Two", "Abstract two text."),
            ]
        }

        docs = fetch_pubmed_docs("test query")

        assert len(docs) == 2
        assert docs[0]["pmid"] == "123"
        assert docs[0]["title"] == "Article One"
        assert "pubmed.ncbi.nlm.nih.gov/123" in docs[0]["url"]
        assert docs[0]["journal"] == "Test Journal"
        assert docs[0]["year"] == 2023
        assert "Abstract one text." in docs[0]["text"]

    @patch("app.ingest._entrez_fetch")
    @patch("app.ingest._entrez_search")
    @patch("app.ingest.time.sleep")
    def test_articles_without_abstracts_skipped(self, mock_sleep, mock_search, mock_fetch):
        mock_search.return_value = {"IdList": ["111", "222"]}
        mock_fetch.return_value = {
            "PubmedArticle": [
                _make_fake_article("111", "Has Abstract", "Some text."),
                {
                    "MedlineCitation": {
                        "PMID": "222",
                        "Article": {
                            "ArticleTitle": "No Abstract",
                            "Abstract": {"AbstractText": ""},
                            "Journal": {"Title": "J", "JournalIssue": {"PubDate": {"Year": "2023"}}},
                        },
                    },
                },
            ]
        }

        docs = fetch_pubmed_docs("test query")
        assert len(docs) == 1
        assert docs[0]["pmid"] == "111"

    @patch("app.ingest._entrez_fetch")
    @patch("app.ingest._entrez_search")
    @patch("app.ingest.time.sleep")
    def test_no_results_returns_empty(self, mock_sleep, mock_search, mock_fetch):
        mock_search.return_value = {"IdList": []}
        docs = fetch_pubmed_docs("obscure query")
        assert docs == []
        mock_fetch.assert_not_called()

    @patch("app.ingest._entrez_fetch")
    @patch("app.ingest._entrez_search")
    @patch("app.ingest.time.sleep")
    def test_entrez_email_set_from_env(self, mock_sleep, mock_search, mock_fetch, monkeypatch):
        monkeypatch.setenv("PUBMED_EMAIL", "test@example.com")
        mock_search.return_value = {"IdList": []}

        fetch_pubmed_docs("query")

        from Bio import Entrez
        assert Entrez.email == "test@example.com"

    @patch("app.ingest._entrez_fetch")
    @patch("app.ingest._entrez_search")
    @patch("app.ingest.time.sleep")
    def test_returns_expected_keys(self, mock_sleep, mock_search, mock_fetch):
        mock_search.return_value = {"IdList": ["999"]}
        mock_fetch.return_value = {
            "PubmedArticle": [
                _make_fake_article("999", "Test Title", "Test abstract."),
            ]
        }

        docs = fetch_pubmed_docs("query")
        expected_keys = {"pmid", "title", "url", "journal", "year", "text"}
        assert set(docs[0].keys()) == expected_keys


# ---------------------------------------------------------------------------
# ingest_text_items (requires mock_settings fixture)
# ---------------------------------------------------------------------------

class TestIngestTextItems:
    def test_empty_items_returns_zero_counts(self, mock_settings):
        result = ingest_text_items([])
        assert result == {"ok": True, "added": 0, "skipped": 0}

    def test_items_with_text_are_ingested(self, mock_settings):
        items = [
            {
                "text": "This is a sufficiently long piece of text for chunking to produce at least one chunk. " * 5,
                "title": "Test Article",
                "url": "https://example.com",
                "pmid": "12345",
                "journal": "Test Journal",
                "year": 2023,
            }
        ]
        result = ingest_text_items(items)
        assert result["ok"] is True
        assert result["added"] > 0
        assert result["skipped"] == 0

    def test_duplicate_pmid_in_same_context_skipped(self, mock_settings):
        items = [
            {
                "text": "First article with enough text to be chunked properly and not be empty. " * 5,
                "pmid": "55555",
                "title": "Article A",
            }
        ]
        # First ingestion
        r1 = ingest_text_items(items)
        assert r1["added"] > 0

        # Second ingestion of the same PMID
        r2 = ingest_text_items(items)
        assert r2["skipped"] > 0
        assert r2["added"] == 0

    def test_items_with_empty_text_skipped(self, mock_settings):
        items = [
            {"text": "", "pmid": "99999", "title": "Empty"},
            {"text": "   ", "pmid": "99998", "title": "Whitespace"},
        ]
        result = ingest_text_items(items)
        assert result["added"] == 0
        assert result["skipped"] == 2

    def test_owner_uid_set_in_metadata(self, mock_settings):
        items = [
            {
                "text": "Article text that is long enough to be chunked and stored properly. " * 5,
                "pmid": "77777",
                "title": "Owned Article",
            }
        ]
        ingest_text_items(items, owner_uid="user-abc")

        from app.rag import get_store
        store = get_store()
        # Check that the metadata has the owner_uid
        found = False
        for md in store._meta:
            if md.get("pmid") == "77777":
                assert "owner_uids" in md
                assert "user-abc" in md["owner_uids"]
                found = True
        assert found, "Expected to find metadata with pmid=77777"

    def test_different_owners_can_ingest_same_pmid(self, mock_settings):
        items = [
            {
                "text": "Shared article text that multiple users might ingest into their own scope. " * 5,
                "pmid": "88888",
                "title": "Shared Article",
            }
        ]
        r1 = ingest_text_items(items, owner_uid="user-one")
        assert r1["added"] > 0

        r2 = ingest_text_items(items, owner_uid="user-two")
        assert r2["added"] > 0
