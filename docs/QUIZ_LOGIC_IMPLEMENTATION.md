# Quiz Logic Implementation Summary

## 🎯 Implementation Complete!

Berhasil mengimplementasikan sistem quiz dengan logic baru sesuai requirement:

### ✅ Core Requirements Implemented

1. **Kedua Tipe Quiz Menggunakan `question_count`**
   - **Subject Quiz**: Random dari semua soal mata pelajaran
   - **Custom Quiz**: Random dari soal yang dipilih (optional)
   
2. **Pre-Generated Attempts**
   - Saat mulai quiz session, Attempt records dibuat dengan jawaban null
   - Saat submit, existing Attempt records di-update (tidak create baru)

3. **Random Question Selection**
   - Subject Quiz: Random `question_count` soal dari bank soal subject
   - Custom Quiz dengan `question_count`: Random `question_count` dari soal terpilih
   - Custom Quiz tanpa `question_count`: Gunakan semua soal terpilih

---

## 📝 Changes Made

### Database Models

#### Quiz Model (`apps/quizzes/models.py`)
```python
# Updated fields
question_count = models.IntegerField(
    help_text="Number of random questions to use per quiz session"
)

# Updated validation
def clean(self):
    if self.quiz_type == SUBJECT_BASED:
        - Must have question_count
        - Cannot have manual questions
    elif self.quiz_type == CUSTOM:
        - Must have at least one question
        - question_count optional (if set, can't exceed available)
```

#### Attempt Model (`apps/analytics/models.py`)
```python
# Made nullable for pre-generation
answer_given = models.TextField(blank=True, default='')
is_correct = models.BooleanField(default=False)
time_taken = models.IntegerField(default=0)
```

#### QuizSession Model (`apps/quizzes/models.py`)
```python
def _populate_session_questions(self):
    """Select questions based on quiz type."""
    if quiz_type == SUBJECT_BASED:
        # Random from subject's question bank
        selected = random.sample(available_questions, question_count)
    elif quiz_type == CUSTOM:
        if question_count:
            # Random subset from selected questions
            selected = random.sample(quiz.questions.all(), question_count)
        else:
            # Use all selected questions
            selected = quiz.questions.all()
    
    # Pre-generate Attempt records
    self._generate_attempts()

def _generate_attempts(self):
    """Pre-generate Attempt records with empty answers."""
    for question in session_questions.all():
        Attempt.objects.get_or_create(
            student=student,
            question=question,
            quiz_session=self,
            defaults={'answer_given': '', 'is_correct': False}
        )
```

### Views

#### `finish_quiz()` method updated
```python
def finish_quiz(self, session, post_data):
    """Update existing Attempt records instead of creating new ones."""
    for question in session.session_questions.all():
        answer_given = post_data.get(f'question_{question.id}')
        
        # Find and update existing Attempt
        attempt = Attempt.objects.get(
            student=session.student,
            question=question,
            quiz_session=session
        )
        
        attempt.answer_given = answer_given
        attempt.is_correct = (answer_given == question.answer_key)
        attempt.save()
```

### Forms

#### CustomQuizBasicForm (new)
```python
class CustomQuizBasicForm(forms.ModelForm):
    fields = ['title', 'description', 'subject', 'grade', 
              'question_count',  # NEW: Optional for random selection
              'time_limit_minutes', 'passing_score']
```

### Migrations

- `analytics.0003_update_quiz_logic`: Alter Attempt fields
- `quizzes.0006_update_quiz_logic`: Update Quiz.question_count help text

---

## 🧪 Test Coverage

### Unit Tests (10 tests) ✅ ALL PASSING
**File**: `apps/quizzes/tests/test_quiz_logic.py`

1. ✅ Subject quiz requires question_count
2. ✅ Subject quiz cannot have manual questions
3. ✅ Custom quiz requires questions
4. ✅ Custom quiz question_count validation
5. ✅ Custom quiz with valid question_count  
6. ✅ Subject quiz selects random questions
7. ✅ Custom quiz with count selects random subset
8. ✅ Custom quiz without count uses all
9. ✅ Session pre-generates attempts
10. ✅ Finish quiz updates existing attempts

### Integration Tests (11 tests) ✅ ALL PASSING
**File**: `apps/quizzes/tests/test_quiz_integration.py`

#### Subject Quiz Creation (3 tests)
- ✅ GET request displays form
- ✅ POST creates subject quiz
- ✅ Validation for missing question_count

#### Custom Quiz Creation (3 tests)
- ✅ Question selection workflow
- ✅ Create with question_count
- ✅ Create without question_count (use all)

#### Quiz Taking Flow (3 tests)
- ✅ Start quiz creates session + attempts
- ✅ Submit quiz updates attempts
- ✅ Score calculation is accurate

#### Randomness (2 tests)
- ✅ Different sessions get different questions
- ✅ Custom quiz random subset works

### E2E Tests (6 tests) 📋 READY
**File**: `tests/e2e/test_quiz_workflows.py`

#### Admin Workflows
- 📋 Create subject quiz full flow
- 📋 Create custom quiz full flow

#### Student Workflows
- 📋 Take quiz and submit answers
- 📋 Quiz session persistence on refresh

#### Results
- 📋 View quiz results after completion

---

## 🚀 How to Run Tests

### Run All Quiz Tests
```bash
# Unit + Integration tests
pytest apps/quizzes/tests/ -v

# E2E tests (requires live server)
pytest tests/e2e/test_quiz_workflows.py -v --headed
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest apps/quizzes/tests/test_quiz_logic.py -v

# Integration tests only
pytest apps/quizzes/tests/test_quiz_integration.py -v

# E2E tests only
pytest tests/e2e/test_quiz_workflows.py -v -m e2e
```

---

## 📊 Test Summary

| Test Type | Count | Status |
|-----------|-------|--------|
| Unit Tests | 10 | ✅ 10/10 PASSING |
| Integration Tests | 11 | ✅ 11/11 PASSING |
| E2E Tests | 6 | 📋 Ready to run |
| **TOTAL** | **27** | **21/21 implemented** |

---

## ✨ Key Features

### For Admins
1. **Subject Quiz**: 
   - Set jumlah soal
   - Soal dipilih random dari bank soal subject saat session dimulai

2. **Custom Quiz**:
   - Pilih soal manual
   - Optional: Set jumlah soal untuk random subset
   - Jika tidak set: Gunakan semua soal terpilih

### For Students
1. **Consistent Experience**:
   - Setiap session mendapat set soal yang konsisten
   - Soal tidak berubah saat refresh page
   
2. **Fair Assessment**:
   - Pre-generated attempts memastikan tidak ada duplicate
   - Score calculation based on actual questions in session

### Database Integrity
1. **No Duplicates**: Attempt.get_or_create prevents duplicate records
2. **Update Not Insert**: Quiz submission updates existing attempts
3. **Referential Integrity**: session_questions tracks actual quiz questions

---

## 🎓 Usage Examples

### Create Subject Quiz
```python
quiz = Quiz.objects.create(
    title="Matematika Kelas 6",
    subject=matematika,
    grade=6,
    quiz_type=Quiz.QuizType.SUBJECT_BASED,
    question_count=10,  # Will select 10 random questions
    time_limit_minutes=30,
    passing_score=70,
    created_by=admin
)
```

### Create Custom Quiz (Random Subset)
```python
quiz = Quiz.objects.create(
    title="Latihan Pecahan",
    subject=matematika,
    grade=6,
    quiz_type=Quiz.QuizType.CUSTOM,
    question_count=5,  # Select 5 random from selected
    created_by=admin
)
quiz.questions.set(selected_questions)  # e.g., 10 questions selected
# Each session will get 5 random from these 10
```

### Create Custom Quiz (Use All)
```python
quiz = Quiz.objects.create(
    title="Ulangan Harian",
    subject=matematika,
    grade=6,
    quiz_type=Quiz.QuizType.CUSTOM,
    question_count=None,  # Use all selected questions
    created_by=admin
)
quiz.questions.set(selected_questions)  # e.g., 8 questions
# Each session will get all 8 questions
```

---

## 🔧 Next Steps

1. ✅ Run all tests to verify everything works
2. ✅ Test in development environment manually
3. 📋 Run E2E tests with actual browser
4. 📋 Update production documentation
5. 📋 Train admins on new quiz creation flow

---

## 📚 Files Modified/Created

### Models
- `apps/quizzes/models.py` (Quiz, QuizSession)
- `apps/analytics/models.py` (Attempt)

### Views
- `apps/quizzes/views.py` (finish_quiz, CustomQuizCreateView)

### Forms
- `apps/quizzes/forms.py` (SubjectQuizForm, CustomQuizBasicForm)

### Templates
- `templates/quizzes/custom_quiz_create.html`
- `templates/quizzes/subject_quiz_create.html`

### Tests (NEW)
- `apps/quizzes/tests/test_quiz_logic.py` (10 unit tests)
- `apps/quizzes/tests/test_quiz_integration.py` (11 integration tests)
- `apps/quizzes/tests/conftest.py` (fixtures)
- `tests/e2e/test_quiz_workflows.py` (6 E2E tests)
- `tests/e2e/conftest.py` (E2E fixtures)

### Migrations
- `apps/analytics/migrations/0003_update_quiz_logic.py`
- `apps/quizzes/migrations/0006_update_quiz_logic.py`
