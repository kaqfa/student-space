import json
from django.db import transaction
from apps.questions.models import Question, Tag
from apps.subjects.models import Subject, Topic
from django.contrib.auth import get_user_model

User = get_user_model()

def import_questions_from_json(json_data, user=None):
    """
    Import questions from a list of dictionaries (parsed JSON).
    Returns a tuple (created_count, errors_list).
    """
    created_count = 0
    errors = []

    if not isinstance(json_data, list):
        return 0, ["JSON root must be a list of objects."]

    with transaction.atomic():
        for index, item in enumerate(json_data):
            try:
                # Required fields
                grade = item.get("grade")
                subject_name = item.get("subject")
                topic_name = item.get("topic")
                text = item.get("text")
                q_type = item.get("type", "pilgan")
                answer = item.get("answer")
                
                if not all([grade, subject_name, topic_name, text, answer]):
                    errors.append(f"Row {index+1}: Missing required fields (grade, subject, topic, text, answer).")
                    continue

                # Find or Create Subject & Topic
                # We assume subject exists to avoid polluting DB with erratic names, 
                # but for Topic we can create if missing.
                
                subject = Subject.objects.filter(name__iexact=subject_name, grade=grade).first()
                if not subject:
                    # Fallback: try finding subject by name only? No, grade is important.
                    errors.append(f"Row {index+1}: Subject '{subject_name}' for Grade {grade} not found.")
                    continue
                
                topic, _ = Topic.objects.get_or_create(
                    subject=subject,
                    name__iexact=topic_name,
                    defaults={"name": topic_name, "description": f"Imported topic {topic_name}"}
                )

                # Prepare Question Data
                q_data = {
                    "topic": topic,
                    "question_text": text,
                    "question_type": q_type,
                    "difficulty": item.get("difficulty", "sedang"),
                    "answer_key": answer,
                    "explanation": item.get("explanation", ""),
                    "created_by": user,
                    "points": item.get("points", 10),
                    "estimated_time": item.get("estimated_time", 60),
                }

                # Options handling
                if q_type == "pilgan":
                    options = item.get("options", [])
                    if not isinstance(options, list) or len(options) < 2:
                        errors.append(f"Row {index+1}: Pilgan must have at least 2 options list.")
                        continue
                    q_data["options"] = options

                # Create Question
                question = Question.objects.create(**q_data)
                
                # Handle Tags (list of strings)
                tags_list = item.get("tags", [])
                if tags_list:
                    for tag_name in tags_list:
                        tag, _ = Tag.objects.get_or_create(name=tag_name)
                        question.tags.add(tag)
                
                created_count += 1

            except Exception as e:
                errors.append(f"Row {index+1}: Error - {str(e)}")

    return created_count, errors
