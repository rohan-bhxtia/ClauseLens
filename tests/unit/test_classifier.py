import pytest
from pydantic import ValidationError

from clauselens.classify import classifier
from clauselens.classify.classifier import (
    DocClassification,
    classify_document,
)


def test_classifier_returns_valid_classification(monkeypatch):
    def fake_router(*args, **kwargs):
        class FakeResult:
            text = (
                '{"doc_type": "residential_lease", '
                '"reason": "Indian residential rental agreement."}'
            )

        return FakeResult()

    monkeypatch.setattr(
        classifier,
        "call_with_fallback",
        fake_router,
    )

    result = classify_document(
        client=None,
        settings=None,
        cache=None,
        first_page_text="Residential rental agreement",
    )

    assert isinstance(result, DocClassification)
    assert result.doc_type == "residential_lease"


def test_classifier_rejects_invalid_json(monkeypatch):
    def fake_router(*args, **kwargs):
        class FakeResult:
            text = '{"doc_type": "invalid_type", "reason": "Test"}'

        return FakeResult()

    monkeypatch.setattr(
        classifier,
        "call_with_fallback",
        fake_router,
    )

    with pytest.raises(ValidationError):
        classify_document(
            client=None,
            settings=None,
            cache=None,
            first_page_text="Some document",
        )