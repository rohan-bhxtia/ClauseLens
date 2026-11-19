
from clauselens.retrieval.questions import QUESTIONS
from clauselens.schemas.lease import LeaseFacts


def test_there_are_15_questions():
    assert len(QUESTIONS) == 15


def test_ids_are_unique():
    ids = [question.id for question in QUESTIONS]
    assert len(ids) == len(set(ids))


def test_ids_match_leasefacts_fields():
    question_ids = {question.id for question in QUESTIONS}
    schema_fields = set(LeaseFacts.model_fields) - {"doc_id"}

    assert question_ids == schema_fields
