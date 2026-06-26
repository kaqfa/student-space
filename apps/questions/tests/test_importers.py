import pytest
from apps.subjects.models import Subject, Topic
from apps.questions.models import Question
from apps.questions.services import import_questions_from_json

pytestmark = pytest.mark.django_db


@pytest.fixture
def subject_topic():
    subject = Subject.objects.create(name="Matematika", grade=3)
    topic = Topic.objects.create(subject=subject, name="Penjumlahan")
    return subject, topic


def test_import_valid_questions(subject_topic):
    data = [{
        "grade": 3, "subject": "Matematika", "topic": "Penjumlahan",
        "text": "1+1?", "type": "pilgan", "answer": "B",
        "options": ["1", "2", "3", "4"],
    }]
    count, errors = import_questions_from_json(data, user=None)
    assert count == 1
    assert errors == []
    assert Question.objects.count() == 1


def test_import_rejects_non_list():
    count, errors = import_questions_from_json({"not": "a list"}, user=None)
    assert count == 0
    assert errors


def test_import_reports_missing_fields(subject_topic):
    data = [{"grade": 3, "subject": "Matematika"}]  # missing topic/text/answer
    count, errors = import_questions_from_json(data, user=None)
    assert count == 0
    assert len(errors) == 1
