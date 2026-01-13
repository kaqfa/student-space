# Technical Specification: Bank Soal SD (Django + PostgreSQL)

**Version:** 2.0  
**Architecture:** Django Monolith + HTMX  
**Last Updated:** 2025-01-11

---

## 1. Technology Stack

### Backend
- **Framework:** Django 5.0.x
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+
- **ORM:** Django ORM
- **Task Queue:** Celery 5.x (optional, untuk heavy analytics)
- **Cache:** Redis 7.x (optional, untuk performance)
- **API:** Django REST Framework 3.14.x (optional, future mobile app)

### Frontend
- **Template Engine:** Django Templates (Jinja2-like)
- **CSS Framework:** Tailwind CSS 3.4.x
- **JavaScript:** HTMX 1.9.x (dynamic interactions)
- **Charts:** Chart.js 4.x
- **Math:** KaTeX 0.16.x (LaTeX rendering)
- **Icons:** Heroicons (Tailwind compatible)

### Deployment
- **App Server:** Gunicorn 21.x
- **Web Server:** Nginx 1.24.x
- **Process Manager:** Systemd
- **OS:** Ubuntu 22.04 LTS
- **SSL:** Let's Encrypt (Certbot)
- **VPS:** Domainesia atau DigitalOcean

### Development Tools
- **Version Control:** Git + GitHub
- **Python Env:** venv (built-in)
- **Package Manager:** pip
- **Code Quality:** Black, Flake8, isort
- **Testing:** pytest, pytest-django
- **Database Client:** pgAdmin 4 atau DBeaver

---

## 2. Project Structure

```
bank_soal_project/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py (future: WebSocket support)
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── decorators.py
│   │   ├── mixins.py
│   │   ├── templates/accounts/
│   │   └── tests/
│   ├── students/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── templates/students/
│   │   └── tests/
│   ├── subjects/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── templates/subjects/
│   │   └── tests/
│   ├── questions/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_questions.py
│   │   ├── utils/
│   │   │   ├── import_handler.py
│   │   │   └── validators.py
│   │   ├── templates/questions/
│   │   └── tests/
│   ├── quizzes/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── quiz_engine.py
│   │   ├── timer.py
│   │   ├── templates/quizzes/
│   │   └── tests/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── metrics.py
│   │   ├── reports.py
│   │   ├── charts.py
│   │   ├── templates/analytics/
│   │   └── tests/
│   └── core/
│       ├── __init__.py
│       ├── mixins.py
│       ├── decorators.py
│       ├── utils.py
│       ├── constants.py
│       └── context_processors.py
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── footer.html
│   │   ├── alerts.html
│   │   ├── pagination.html
│   │   └── question_card.html
│   ├── partials/ (HTMX partials)
│   │   ├── quiz_question.html
│   │   ├── progress_chart.html
│   │   └── analytics_widget.html
│   └── errors/
│       ├── 404.html
│       ├── 500.html
│       └── 403.html
├── static/
│   ├── css/
│   │   ├── input.css (Tailwind source)
│   │   └── output.css (Tailwind compiled)
│   ├── js/
│   │   ├── htmx.min.js
│   │   ├── chart.js
│   │   ├── katex.min.js
│   │   ├── quiz-timer.js
│   │   └── app.js (custom JS)
│   ├── images/
│   │   └── logo.svg
│   └── icons/ (Heroicons)
├── media/
│   ├── questions/
│   │   └── images/
│   └── uploads/
├── staticfiles/ (collectstatic output)
├── locale/ (i18n, future)
├── logs/
│   ├── django.log
│   └── errors.log
├── scripts/
│   ├── import_questions.py (standalone script)
│   ├── backup_db.sh
│   └── deploy.sh
├── docs/
│   ├── PRD.md
│   ├── TECHNICAL_SPEC.md
│   ├── API.md (if DRF)
│   └── DEPLOYMENT.md
├── .env.example
├── .gitignore
├── .flake8
├── .black
├── pytest.ini
├── tailwind.config.js
├── package.json (for Tailwind)
└── README.md
```

---

## 3. Database Schema (Detailed)

### 3.1 User & Authentication

#### User (Django AbstractUser)
```python
# Built-in Django User model, extended
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('parent', 'Parent'),  # Orang tua / Guru / Pengajar
        ('student', 'Student'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    grade = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(6)])  # Only for students
    date_of_birth = models.DateField(null=True, blank=True)  # Only for students
    
    class Meta:
        db_table = 'users'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_parent(self):
        return self.role == 'parent'
    
    @property
    def is_student(self):
        return self.role == 'student'
```

**Fields:**
- id (PK, AutoField)
- username (CharField, unique, max_length=150)
- email (EmailField, unique)
- password (CharField, hashed)
- first_name (CharField, max_length=150)
- last_name (CharField, max_length=150)
- role (CharField, max_length=20) - admin, parent, student
- avatar (ImageField)
- phone (CharField, max_length=20)
- grade (IntegerField, 1-6, nullable) - hanya untuk student
- date_of_birth (DateField, nullable) - hanya untuk student
- is_active (BooleanField, default=True)
- is_staff (BooleanField, default=False)
- is_superuser (BooleanField, default=False)
- date_joined (DateTimeField, auto_now_add=True)
- last_login (DateTimeField, null=True)

**Indexes:**
- email (unique)
- username (unique)
- role
- grade (for students filtering)

---

### 3.2 Parent-Student Relationship

#### ParentStudent (Linking Table with Verification)
```python
class ParentStudent(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_links', limit_choices_to={'role': 'parent'})
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_links', limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by_parent = models.BooleanField(default=False)  # True jika parent yang buat akun student
    notes = models.TextField(blank=True)  # Notes dari parent tentang student
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'parent_students'
        unique_together = ['parent', 'student']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent', 'status']),
            models.Index(fields=['student', 'status']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} → {self.student.get_full_name()} ({self.status})"
    
    def approve(self):
        self.status = 'approved'
        self.verified_at = timezone.now()
        self.save()
    
    def reject(self):
        self.status = 'rejected'
        self.save()
```

**Relationship Flow:**
1. **Parent creates new student:** Parent buat akun student → `created_by_parent=True`, `status='approved'` (auto-approved)
2. **Parent links existing student:** Parent request link → `status='pending'` → Student verify → `status='approved'` / `status='rejected'`
3. **Student independent:** Student bisa menggunakan app tanpa relasi ke parent mana pun

**Fields:**
- id (PK)
- parent_id (FK → User, parent role)
- student_id (FK → User, student role)
- status (pending, approved, rejected)
- created_by_parent (Boolean) - true jika parent yang buat akun
- notes (TextField) - catatan parent tentang student
- created_at (DateTimeField)
- verified_at (DateTimeField, nullable)

**Indexes:**
- unique_together: (parent, student)
- (parent, status)
- (student, status)

---

### 3.3 Subjects & Topics

#### Subject
```python
class Subject(models.Model):
    name = models.CharField(max_length=100)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True)  # Icon name from Heroicons
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subjects'
        ordering = ['grade', 'order', 'name']
        unique_together = ['name', 'grade']
        indexes = [
            models.Index(fields=['grade', 'order']),
        ]
    
    def __str__(self):
        return f"{self.name} (Kelas {self.grade})"
```

#### Topic
```python
class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['subject', 'order', 'name']
        indexes = [
            models.Index(fields=['subject', 'order']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
```

---

### 3.4 Curriculum & Tags

#### KompetensiDasar
```python
class KompetensiDasar(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g., "3.1", "4.2"
    description = models.TextField()
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='kompetensi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kompetensi_dasar'
        verbose_name = 'Kompetensi Dasar'
        verbose_name_plural = 'Kompetensi Dasar'
        ordering = ['grade', 'subject', 'code']
        indexes = [
            models.Index(fields=['grade', 'subject']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.description[:50]}"
```

#### Tag
```python
class Tag(models.Model):
    CATEGORY_CHOICES = [
        ('skill', 'Skill'),
        ('topic', 'Topic'),
        ('difficulty', 'Difficulty'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name
```

---

### 3.5 Questions

#### Question
```python
class Question(models.Model):
    TYPE_CHOICES = [
        ('pilgan', 'Pilihan Ganda'),
        ('essay', 'Essay'),
        ('isian', 'Isian'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('mudah', 'Mudah'),
        ('sedang', 'Sedang'),
        ('sulit', 'Sulit'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # For pilgan
    options = models.JSONField(null=True, blank=True)  # ["A. ...", "B. ...", "C. ...", "D. ..."]
    
    answer_key = models.TextField()
    explanation = models.TextField()
    
    # Media & formatting
    has_image = models.BooleanField(default=False)
    image = models.ImageField(upload_to='questions/images/', null=True, blank=True)
    has_math = models.BooleanField(default=False)
    
    # Metadata
    estimated_time = models.IntegerField(default=60, help_text='Estimated time in seconds')
    points = models.IntegerField(default=10)
    order = models.IntegerField(default=0)
    
    # Relations
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)
    kompetensi_dasar = models.ManyToManyField(KompetensiDasar, related_name='questions', blank=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['topic', 'order']
        indexes = [
            models.Index(fields=['topic', 'difficulty']),
            models.Index(fields=['question_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"
    
    def get_subject(self):
        return self.topic.subject
```

---

### 3.6 Quizzes

#### QuizSession
```python
class QuizSession(models.Model):
    TYPE_CHOICES = [
        ('practice', 'Practice Mode'),
        ('timed', 'Timed Quiz'),
        ('custom', 'Custom Quiz'),
    ]
    
    # Student who takes the quiz (User with role='student')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions', limit_choices_to={'role': 'student'})
    quiz_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    
    # Grade filter - untuk filter mata pelajaran yang tersedia di grade tersebut
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)], help_text='Kelas untuk filter mata pelajaran')
    
    # Timing
    time_limit = models.IntegerField(null=True, blank=True, help_text='Total time limit in seconds')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    
    # Scoring
    total_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    
    # Quiz creator (for custom quiz or proxy mode)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_quizzes')
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Proxy Quiz Mode - Parent runs quiz on behalf of student
    is_proxy_mode = models.BooleanField(default=False, help_text='True jika quiz dijalankan oleh parent atas nama student')
    proxy_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proxy_quizzes', help_text='Parent yang menjalankan proxy quiz')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_completed']),
            models.Index(fields=['grade']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        prefix = "[PROXY] " if self.is_proxy_mode else ""
        return f"{prefix}{self.student.get_full_name()} - {self.get_quiz_type_display()} ({self.created_at.date()})"
    
    def calculate_score(self):
        attempts = self.attempts.all()
        self.total_score = sum(a.points_earned for a in attempts)
        self.max_score = sum(a.question.points for a in attempts)
        self.save()
    
    def save(self, *args, **kwargs):
        # Default grade to student's grade if not set
        if not self.grade and self.student and self.student.grade:
            self.grade = self.student.grade
        super().save(*args, **kwargs)
```

#### QuizQuestion (Through model for M2M)
```python
class QuizQuestion(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='quiz_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField()
    time_allocated = models.IntegerField(null=True, blank=True, help_text='Time allocated for this question in seconds')
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['quiz_session', 'order']
        unique_together = ['quiz_session', 'question']
```

---

### 3.7 Analytics & Progress

#### Attempt
```python
class Attempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts', limit_choices_to={'role': 'student'})
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts')
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, null=True, blank=True, related_name='attempts')
    
    answer_given = models.TextField()
    is_correct = models.BooleanField()
    time_taken = models.IntegerField(help_text='Time taken in seconds')
    points_earned = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['student', 'question']),
            models.Index(fields=['quiz_session']),
            models.Index(fields=['is_correct']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Q{self.question.id} ({'✓' if self.is_correct else '✗'})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate points
        if self.is_correct:
            self.points_earned = self.question.points
        else:
            self.points_earned = 0
        super().save(*args, **kwargs)
```

---

## 4. Django Apps Detail

### 4.1 accounts

**Purpose:** User management, authentication, authorization, registration

**Models:**
- User (custom with role: admin, parent, student)
- ParentStudent (linking table with verification)

**Views:**
- LoginView (login page)
- LogoutView (logout)
- RegisterView (student self-registration)
- ProfileView (user profile)
- PasswordChangeView (change password)
- LinkRequestListView (student: view pending link requests from parents)
- LinkRequestActionView (student: approve/reject link request)

**Forms:**
- LoginForm
- StudentRegistrationForm (student self-registration)
- ParentRegistrationForm (parent registration)
- UserUpdateForm
- PasswordChangeForm
- LinkRequestForm (parent request link to existing student)

**Decorators:**
- `@admin_required`
- `@parent_required`
- `@parent_or_admin_required`
- `@student_required`
- `@login_required`

**Mixins:**
- `AdminRequiredMixin`
- `ParentRequiredMixin`
- `ParentOrAdminMixin`
- `StudentRequiredMixin`

**URLs:**
- `/accounts/login/` - login
- `/accounts/logout/` - logout
- `/accounts/register/` - student registration
- `/accounts/register/parent/` - parent registration
- `/accounts/profile/` - user profile
- `/accounts/password/change/` - change password
- `/accounts/link-requests/` - student: view link requests
- `/accounts/link-requests/<pk>/action/` - student: approve/reject

---

### 4.2 students (Parent's Student Management)

**Purpose:** Parent manages their linked students, proxy quiz

**Models:**
- (Uses User with role='student' and ParentStudent linking)

**Views:**
- MyStudentsListView (parent: list all linked students)
- StudentDetailView (parent: view student profile & progress)
- StudentCreateView (parent: create new student account for their child)
- StudentLinkView (parent: request link to existing student)
- StudentDashboardView (student's own dashboard)
- SelectStudentForQuizView (parent: select student before proxy quiz)

**Forms:**
- CreateStudentForm (parent creates new student account)
- LinkStudentForm (parent requests link to existing student)

**URLs:**
- `/my-students/` - parent: list linked students
- `/my-students/<pk>/` - parent: student detail & progress
- `/my-students/create/` - parent: create new student account
- `/my-students/link/` - parent: request link to existing student
- `/dashboard/` - student: own dashboard
- `/my-students/<pk>/quiz/` - parent: select student for proxy quiz

---

### 4.3 subjects

**Purpose:** Subject and topic management

**Models:**
- Subject
- Topic

**Views:**
- SubjectListView (list subjects by grade)
- TopicListView (list topics for a subject)
- TopicDetailView (topic detail with questions)

**Admin:**
- SubjectAdmin (inline topics)
- TopicAdmin

**URLs:**
- `/subjects/` - subject list
- `/subjects/<pk>/topics/` - topics in subject
- `/topics/<pk>/` - topic detail

---

### 4.4 questions

**Purpose:** Question bank management, tagging, bulk import

**Models:**
- Question
- Tag
- KompetensiDasar

**Views:**
- QuestionListView (with filters)
- QuestionDetailView
- QuestionCreateView
- QuestionUpdateView
- QuestionDeleteView
- QuestionImportView (JSON upload)
- TagListView
- TagCreateView
- KDListView
- KDCreateView

**Forms:**
- QuestionForm
- QuestionFilterForm
- QuestionImportForm (file upload)
- TagForm
- KDForm

**Utils:**
- `import_handler.py` - handle JSON parsing & validation
- `validators.py` - validate question data

**Management Commands:**
```bash
python manage.py import_questions data/matematika-kelas6.json
```

**Admin:**
- QuestionAdmin (advanced filters, inline tags/KD)
- TagAdmin
- KDAdmin

**URLs:**
- `/questions/` - list
- `/questions/<pk>/` - detail
- `/questions/create/` - create
- `/questions/<pk>/edit/` - edit
- `/questions/import/` - bulk import
- `/tags/` - tag management
- `/kompetensi/` - KD management

---

### 4.5 quizzes

**Purpose:** Quiz creation, taking, scoring

**Models:**
- QuizSession
- QuizQuestion

**Views:**
- QuizListView (available quizzes for student)
- QuizCreateView (admin/pengajar create custom quiz)
- QuizConfigView (configure quiz settings before start)
- QuizTakeView (main quiz interface - HTMX heavy)
- QuizResultView (results after completion)
- QuizReviewView (review quiz with explanations)

**Forms:**
- CustomQuizForm (create custom quiz)
- QuizConfigForm (configure filters, time, etc)

**quiz_engine.py:**
```python
class QuizEngine:
    def create_quiz_session(student, quiz_type, config):
        """Create new quiz session with questions"""
        pass
    
    def get_next_question(quiz_session):
        """Get next unanswered question"""
        pass
    
    def submit_answer(quiz_session, question, answer, time_taken):
        """Record attempt and validate answer"""
        pass
    
    def complete_quiz(quiz_session):
        """Mark quiz complete and calculate final score"""
        pass
```

**timer.py:**
```python
class QuizTimer:
    def get_remaining_time(quiz_session):
        """Calculate remaining time for timed quiz"""
        pass
    
    def is_time_expired(quiz_session):
        """Check if time limit exceeded"""
        pass
```

**URLs:**
- `/quizzes/` - list available quizzes
- `/quizzes/create/` - create custom quiz
- `/quizzes/<pk>/config/` - configure quiz
- `/quizzes/<pk>/start/` - start quiz
- `/quizzes/<pk>/take/` - quiz interface (HTMX)
- `/quizzes/<pk>/result/` - results
- `/quizzes/<pk>/review/` - review

---

### 4.6 analytics

**Purpose:** Progress tracking, analytics, reporting

**Models:**
- Attempt

**Views:**
- ProgressDashboardView (student progress overview)
- AnalyticsDashboardView (admin/pengajar detailed analytics)
- SubjectAnalyticsView (analytics per subject)
- TopicAnalyticsView (analytics per topic)
- TagAnalyticsView (skill heatmap)
- KDAnalyticsView (curriculum coverage)
- ReportGenerateView (generate PDF/CSV report)

**metrics.py:**
```python
class ProgressMetrics:
    @staticmethod
    def calculate_accuracy(student, subject=None, topic=None):
        """Calculate accuracy rate"""
        pass
    
    @staticmethod
    def calculate_mastery_level(student, topic):
        """Determine mastery level"""
        pass
    
    @staticmethod
    def get_strengths_weaknesses(student):
        """Identify strong and weak tags"""
        pass
    
    @staticmethod
    def get_kd_coverage(student, grade):
        """Calculate KD coverage percentage"""
        pass
```

**reports.py:**
```python
class ReportGenerator:
    def generate_progress_report(student, date_range):
        """Generate progress report"""
        pass
    
    def generate_performance_report(student):
        """Generate performance report"""
        pass
    
    def export_to_pdf(report_data):
        """Export report to PDF"""
        pass
    
    def export_to_csv(report_data):
        """Export report to CSV"""
        pass
```

**charts.py:**
```python
class ChartData:
    @staticmethod
    def accuracy_over_time(student, days=30):
        """Data for accuracy trend chart"""
        pass
    
    @staticmethod
    def subject_distribution(student):
        """Data for subject performance pie chart"""
        pass
    
    @staticmethod
    def tag_heatmap(student):
        """Data for skill heatmap"""
        pass
```

**URLs:**
- `/analytics/progress/` - student progress dashboard
- `/analytics/dashboard/` - admin analytics dashboard
- `/analytics/subject/<pk>/` - subject analytics
- `/analytics/topic/<pk>/` - topic analytics
- `/analytics/tags/` - tag analytics (heatmap)
- `/analytics/kd/` - KD coverage
- `/analytics/report/generate/` - generate report

---

## 5. HTMX Integration

### 5.1 HTMX Use Cases

**Quiz Taking:**
```html
<!-- Quiz question with HTMX -->
<div id="quiz-question" hx-get="/quizzes/{{ quiz.id }}/next-question/" hx-trigger="load">
    <!-- Question loads here -->
</div>

<!-- Submit answer via HTMX -->
<form hx-post="/quizzes/{{ quiz.id }}/submit/" hx-target="#quiz-question">
    <input type="radio" name="answer" value="A">
    <button type="submit">Submit</button>
</form>
```

**Live Timer:**
```html
<!-- Timer updates via polling -->
<div id="timer" 
     hx-get="/quizzes/{{ quiz.id }}/timer/" 
     hx-trigger="every 1s"
     hx-swap="innerHTML">
    10:00
</div>
```

**Analytics Charts:**
```html
<!-- Load chart data asynchronously -->
<div hx-get="/analytics/chart/accuracy/" 
     hx-trigger="load" 
     hx-swap="innerHTML">
    Loading...
</div>
```

**Question Filters:**
```html
<!-- Filter questions without page reload -->
<form hx-get="/questions/" 
      hx-target="#question-list" 
      hx-trigger="change from:select">
    <select name="difficulty">
        <option value="">All</option>
        <option value="mudah">Mudah</option>
    </select>
</form>

<div id="question-list">
    <!-- Filtered questions load here -->
</div>
```

### 5.2 HTMX Response Patterns

**Partial Template:**
```python
# views.py
def next_question(request, quiz_id):
    question = quiz_engine.get_next_question(quiz_id)
    return render(request, 'partials/quiz_question.html', {'question': question})
```

**Trigger Events:**
```python
# Trigger custom event after answer submission
from django.http import HttpResponse

def submit_answer(request, quiz_id):
    # ... process answer
    response = render(request, 'partials/quiz_question.html', context)
    response['HX-Trigger'] = 'answerSubmitted'
    return response
```

---

## 6. Frontend Architecture

### 6.1 Tailwind CSS Setup

**tailwind.config.js:**
```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

**Build Command:**
```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

### 6.2 Base Template

**templates/base.html:**
```html
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Bank Soal SD{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <link rel="stylesheet" href="{% static 'css/output.css' %}">
    
    <!-- HTMX -->
    <script src="{% static 'js/htmx.min.js' %}" defer></script>
    
    <!-- Chart.js -->
    <script src="{% static 'js/chart.js' %}" defer></script>
    
    <!-- KaTeX (for math) -->
    <link rel="stylesheet" href="{% static 'css/katex.min.css' %}">
    <script src="{% static 'js/katex.min.js' %}" defer></script>
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    {% include 'components/navbar.html' %}
    
    <div class="flex">
        {% if user.is_authenticated %}
            {% include 'components/sidebar.html' %}
        {% endif %}
        
        <main class="flex-1 p-6">
            {% if messages %}
                {% include 'components/alerts.html' %}
            {% endif %}
            
            {% block content %}{% endblock %}
        </main>
    </div>
    
    {% include 'components/footer.html' %}
    
    <script src="{% static 'js/app.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6.3 Component Examples

**Question Card:**
```html
<!-- components/question_card.html -->
<div class="bg-white rounded-lg shadow-md p-6 mb-4">
    <div class="flex justify-between items-start mb-4">
        <h3 class="text-lg font-semibold text-gray-900">
            {{ question.question_text|truncatewords:15 }}
        </h3>
        <span class="px-3 py-1 text-sm rounded-full
                     {% if question.difficulty == 'mudah' %}bg-green-100 text-green-800
                     {% elif question.difficulty == 'sedang' %}bg-yellow-100 text-yellow-800
                     {% else %}bg-red-100 text-red-800{% endif %}">
            {{ question.get_difficulty_display }}
        </span>
    </div>
    
    <div class="flex items-center space-x-4 text-sm text-gray-600">
        <span>{{ question.topic.name }}</span>
        <span>{{ question.get_question_type_display }}</span>
        <span>~{{ question.estimated_time }}s</span>
    </div>
    
    <div class="mt-4">
        <a href="{% url 'questions:detail' question.pk %}" 
           class="text-primary hover:underline">
            Lihat Detail →
        </a>
    </div>
</div>
```

### 6.4 UI Component Library (Phase 7)

**Design Reference:** [Spike Admin React Tailwind](https://spike-react-tailwind-main.netlify.app/)

#### 6.4.1 Layout Templates

**templates/layouts/base_admin.html:**
```html
{% load static %}
<!DOCTYPE html>
<html lang="id" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Bank Soal SD{% endblock %}</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Styles -->
    <link rel="stylesheet" href="{% static 'css/dist/styles.css' %}">
    {% block extra_css %}{% endblock %}
    
    <!-- HTMX -->
    <script src="{% static 'js/htmx.min.js' %}" defer></script>
    <script src="{% static 'js/alpine.min.js' %}" defer></script>
</head>
<body class="bg-slate-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <div class="flex h-screen overflow-hidden" x-data="{ sidebarOpen: false }">
        <!-- Sidebar -->
        {% include 'components/sidebar.html' %}
        
        <!-- Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Top Navbar -->
            {% include 'components/navbar.html' %}
            
            <!-- Page Content -->
            <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
                {% if messages %}
                <div class="mb-6 space-y-2">
                    {% for message in messages %}
                    <div class="p-4 rounded-xl {% if message.tags == 'error' %}bg-red-100 text-red-700{% elif message.tags == 'success' %}bg-green-100 text-green-700{% else %}bg-blue-100 text-blue-700{% endif %}">
                        {{ message }}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="{% static 'js/app.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 6.4.2 Reusable Partials

**templates/partials/card.html:**
```html
{# Usage: {% include 'partials/card.html' with title="Title" subtitle="Subtitle" %} #}
<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 {{ extra_class }}">
    {% if title %}
    <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
        {% if subtitle %}
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ subtitle }}</p>
        {% endif %}
    </div>
    {% endif %}
    <div class="p-6">
        {{ content }}
    </div>
</div>
```

**templates/partials/page_header.html:**
```html
{# Usage: {% include 'partials/page_header.html' with title="Page Title" subtitle="Description" %} #}
<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
    <div>
        {% if back_url %}
        <a href="{{ back_url }}" class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-2">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Kembali
        </a>
        {% endif %}
        <h1 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{{ title }}</h1>
        {% if subtitle %}
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ subtitle }}</p>
        {% endif %}
    </div>
    {% if actions %}
    <div class="mt-4 sm:mt-0 flex items-center gap-2">
        {{ actions }}
    </div>
    {% endif %}
</div>
```

**templates/partials/badge.html:**
```html
{# Usage: {% include 'partials/badge.html' with type="success" text="Active" %} #}
{% with base_class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" %}
<span class="{{ base_class }}
    {% if type == 'success' %}bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300
    {% elif type == 'warning' %}bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300
    {% elif type == 'danger' %}bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300
    {% elif type == 'info' %}bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300
    {% else %}bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300{% endif %}">
    {{ text }}
</span>
{% endwith %}
```

**templates/partials/empty_state.html:**
```html
{# Usage: {% include 'partials/empty_state.html' with icon="users" title="No Data" message="Start by adding new item" action_url="/create/" action_text="Add New" %} #}
<div class="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700">
    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        {% if icon == 'users' %}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
        {% elif icon == 'document' %}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        {% else %}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        {% endif %}
    </svg>
    <h3 class="mt-4 text-sm font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ message }}</p>
    {% if action_url and action_text %}
    <div class="mt-6">
        <a href="{{ action_url }}" class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            {{ action_text }}
        </a>
    </div>
    {% endif %}
</div>
```

#### 6.4.3 Sidebar Component

**templates/components/sidebar.html:**
```html
{# Sidebar navigation dengan Alpine.js untuk interaktivitas #}
<aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 
              fixed inset-y-0 left-0 z-50 transform transition-transform duration-300
              lg:relative lg:translate-x-0"
       :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'">
    
    <!-- Logo -->
    <div class="h-16 flex items-center px-6 border-b border-gray-200 dark:border-gray-700">
        <span class="text-xl font-bold text-blue-600">Bank Soal SD</span>
    </div>
    
    <!-- Navigation -->
    <nav class="p-4 space-y-1">
        <!-- Section: HOME -->
        <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Home</p>
        
        <a href="{% url 'home' %}" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg
                  {% if request.resolver_match.url_name == 'home' %}bg-blue-50 text-blue-600{% else %}text-gray-700 hover:bg-gray-100{% endif %}">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            Dashboard
        </a>
        
        <!-- Section: APPS -->
        <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-6">Apps</p>
        
        {% if user.is_admin_or_pengajar %}
        <a href="{% url 'students:list' %}" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-100">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
            </svg>
            Siswa
        </a>
        {% endif %}
        
        <a href="{% url 'questions:list' %}" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-100">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Bank Soal
        </a>
        
        <a href="{% url 'quizzes:list' %}" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-100">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
            </svg>
            Kuis
        </a>
    </nav>
    
    <!-- User Info (Bottom) -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
            <img class="w-10 h-10 rounded-full" src="{{ user.avatar.url|default:'/static/images/default-avatar.png' }}" alt="{{ user.username }}">
            <div class="ml-3">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ user.get_full_name|default:user.username }}</p>
                <p class="text-xs text-gray-500">{{ user.get_role_display }}</p>
            </div>
        </div>
    </div>
</aside>
```

#### 6.4.4 Updated Tailwind Config

**tailwind.config.js (Phase 7 Update):**
```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Spike Admin inspired palette
        primary: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          500: '#5D87FF',
          600: '#4B70E5',
          700: '#3A5ACC',
        },
        success: '#13DEB9',
        warning: '#FFAE1F',
        danger: '#FA896B',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

---

## 7. Import JSON Functionality

### 7.1 JSON Structure

```json
{
  "metadata": {
    "subject": "Matematika",
    "grade": 6,
    "topic": "Pecahan dan Desimal",
    "created_by": "admin",
    "import_date": "2025-01-11"
  },
  "questions": [
    {
      "question_text": "Hasil dari 1/2 + 1/4 adalah...",
      "question_type": "pilgan",
      "difficulty": "mudah",
      "options": [
        "A. 1/2",
        "B. 3/4",
        "C. 1/4",
        "D. 1"
      ],
      "answer_key": "B",
      "explanation": "1/2 + 1/4 = 2/4 + 1/4 = 3/4",
      "tags": ["operasi-hitung", "pecahan-sederhana"],
      "kompetensi_dasar": ["3.1"],
      "has_image": false,
      "has_math": true,
      "estimated_time": 60,
      "points": 10,
      "order": 1
    }
  ]
}
```

### 7.2 Import Handler

**questions/utils/import_handler.py:**
```python
import json
from django.core.exceptions import ValidationError
from apps.questions.models import Question, Tag, KompetensiDasar
from apps.subjects.models import Subject, Topic

class QuestionImporter:
    def __init__(self, json_data, user):
        self.json_data = json_data
        self.user = user
        self.imported_count = 0
        self.errors = []
        self.created_tags = []
    
    def validate(self):
        """Validate JSON structure"""
        required_fields = ['metadata', 'questions']
        for field in required_fields:
            if field not in self.json_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate each question
        for idx, q in enumerate(self.json_data['questions']):
            self._validate_question(q, idx)
    
    def _validate_question(self, question_data, index):
        """Validate single question data"""
        required = ['question_text', 'question_type', 'difficulty', 
                   'answer_key', 'explanation']
        
        for field in required:
            if field not in question_data:
                self.errors.append(f"Question {index+1}: Missing field '{field}'")
        
        # Validate question_type
        if question_data.get('question_type') not in ['pilgan', 'essay', 'isian']:
            self.errors.append(f"Question {index+1}: Invalid question_type")
        
        # Validate pilgan has options
        if question_data.get('question_type') == 'pilgan':
            if not question_data.get('options'):
                self.errors.append(f"Question {index+1}: Pilgan must have options")
    
    def import_questions(self):
        """Import all questions"""
        if self.errors:
            raise ValidationError(self.errors)
        
        # Get or create subject & topic
        metadata = self.json_data['metadata']
        subject = self._get_or_create_subject(metadata)
        topic = self._get_or_create_topic(metadata, subject)
        
        # Import each question
        for q_data in self.json_data['questions']:
            try:
                self._import_question(q_data, topic)
                self.imported_count += 1
            except Exception as e:
                self.errors.append(f"Failed to import question: {str(e)}")
        
        return {
            'imported': self.imported_count,
            'errors': self.errors,
            'created_tags': self.created_tags
        }
    
    def _get_or_create_subject(self, metadata):
        """Get or create subject"""
        subject, created = Subject.objects.get_or_create(
            name=metadata['subject'],
            grade=metadata['grade'],
            defaults={'order': 0}
        )
        return subject
    
    def _get_or_create_topic(self, metadata, subject):
        """Get or create topic"""
        topic, created = Topic.objects.get_or_create(
            subject=subject,
            name=metadata['topic'],
            defaults={'order': 0}
        )
        return topic
    
    def _import_question(self, q_data, topic):
        """Import single question"""
        # Create question
        question = Question.objects.create(
            topic=topic,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            difficulty=q_data['difficulty'],
            options=q_data.get('options'),
            answer_key=q_data['answer_key'],
            explanation=q_data['explanation'],
            has_image=q_data.get('has_image', False),
            has_math=q_data.get('has_math', False),
            estimated_time=q_data.get('estimated_time', 60),
            points=q_data.get('points', 10),
            order=q_data.get('order', 0),
            created_by=self.user
        )
        
        # Add tags
        if 'tags' in q_data:
            for tag_name in q_data['tags']:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'category': 'custom'}
                )
                if created:
                    self.created_tags.append(tag_name)
                question.tags.add(tag)
        
        # Add KD
        if 'kompetensi_dasar' in q_data:
            for kd_code in q_data['kompetensi_dasar']:
                try:
                    kd = KompetensiDasar.objects.get(code=kd_code)
                    question.kompetensi_dasar.add(kd)
                except KompetensiDasar.DoesNotExist:
                    self.errors.append(f"KD {kd_code} not found")
        
        return question
```

### 7.3 Management Command

**questions/management/commands/import_questions.py:**
```python
from django.core.management.base import BaseCommand
from apps.questions.utils.import_handler import QuestionImporter
from apps.accounts.models import User
import json

class Command(BaseCommand):
    help = 'Import questions from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to JSON file')
        parser.add_argument('--user', type=str, default='admin', help='Username of creator')
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        username = options['user']
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
            return
        
        # Read JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Import
        importer = QuestionImporter(data, user)
        
        try:
            importer.validate()
            result = importer.import_questions()
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {result["imported"]} questions'
            ))
            
            if result['created_tags']:
                self.stdout.write(f'Created tags: {", ".join(result["created_tags"])}')
            
            if result['errors']:
                self.stdout.write(self.style.WARNING('Errors:'))
                for error in result['errors']:
                    self.stdout.write(f'  - {error}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
```

**Usage:**
```bash
python manage.py import_questions data/matematika-kelas6-pecahan.json
python manage.py import_questions data/ipa-kelas3.json --user=admin
```

---

## 8. Security & Performance

### 8.1 Security Measures

**settings/production.py:**
```python
DEBUG = False
ALLOWED_HOSTS = ['banksoal.yourdomain.com', 'www.banksoal.yourdomain.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 8.2 Performance Optimization

**Database Indexing:**
- Already defined in model Meta classes
- Use `db_index=True` for frequently queried fields
- Composite indexes for common filter combinations

**Query Optimization:**
```python
# Use select_related for FK
questions = Question.objects.select_related('topic', 'topic__subject')

# Use prefetch_related for M2M
questions = Question.objects.prefetch_related('tags', 'kompetensi_dasar')

# Use only() to limit fields
questions = Question.objects.only('question_text', 'difficulty')

# Use values() for raw data
data = Attempt.objects.values('student_id', 'is_correct').filter(...)
```

**Caching (Optional with Redis):**
```python
from django.core.cache import cache

# Cache expensive queries
def get_student_analytics(student_id):
    cache_key = f'analytics_{student_id}'
    data = cache.get(cache_key)
    
    if not data:
        data = calculate_analytics(student_id)
        cache.set(cache_key, data, timeout=300)  # 5 minutes
    
    return data
```

**Pagination:**
```python
from django.core.paginator import Paginator

def question_list(request):
    questions = Question.objects.all()
    paginator = Paginator(questions, 20)  # 20 per page
    
    page = request.GET.get('page')
    questions = paginator.get_page(page)
    
    return render(request, 'questions/list.html', {'questions': questions})
```

---

## 9. Testing Strategy

### 9.1 Test Structure

```
apps/questions/tests/
├── __init__.py
├── test_models.py
├── test_views.py
├── test_forms.py
├── test_import.py
└── test_utils.py
```

### 9.2 Sample Tests

**test_models.py:**
```python
import pytest
from apps.questions.models import Question
from apps.subjects.models import Subject, Topic

@pytest.mark.django_db
class TestQuestionModel:
    def test_create_question(self):
        subject = Subject.objects.create(name='Matematika', grade=6)
        topic = Topic.objects.create(subject=subject, name='Pecahan')
        
        question = Question.objects.create(
            topic=topic,
            question_text='Test question',
            question_type='pilgan',
            difficulty='mudah',
            answer_key='A',
            explanation='Test explanation'
        )
        
        assert question.id is not None
        assert question.get_subject() == subject
    
    def test_question_str(self):
        subject = Subject.objects.create(name='Matematika', grade=6)
        topic = Topic.objects.create(subject=subject, name='Pecahan')
        question = Question.objects.create(
            topic=topic,
            question_text='What is 1+1?',
            question_type='pilgan',
            difficulty='mudah',
            answer_key='2',
            explanation='1+1=2'
        )
        
        assert 'Pecahan' in str(question)
        assert 'What is 1+1?' in str(question)
```

**test_import.py:**
```python
import pytest
import json
from apps.questions.utils.import_handler import QuestionImporter
from apps.accounts.models import User

@pytest.mark.django_db
class TestQuestionImport:
    def test_import_valid_json(self):
        user = User.objects.create_user(username='test', password='test')
        
        data = {
            'metadata': {
                'subject': 'Matematika',
                'grade': 6,
                'topic': 'Pecahan'
            },
            'questions': [
                {
                    'question_text': 'Test?',
                    'question_type': 'pilgan',
                    'difficulty': 'mudah',
                    'options': ['A. 1', 'B. 2'],
                    'answer_key': 'A',
                    'explanation': 'Test'
                }
            ]
        }
        
        importer = QuestionImporter(data, user)
        importer.validate()
        result = importer.import_questions()
        
        assert result['imported'] == 1
        assert len(result['errors']) == 0
```

---

## 10. Deployment Configuration

### 10.1 Gunicorn Config

**gunicorn_config.py:**
```python
bind = '127.0.0.1:8000'
workers = 3  # 2 * CPU cores + 1
worker_class = 'sync'
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '/home/banksoal/logs/gunicorn_access.log'
errorlog = '/home/banksoal/logs/gunicorn_error.log'
loglevel = 'info'
```

### 10.2 Systemd Service

**/etc/systemd/system/banksoal.service:**
```ini
[Unit]
Description=Bank Soal SD Gunicorn
After=network.target

[Service]
Type=notify
User=banksoal
Group=www-data
WorkingDirectory=/home/banksoal/app
Environment="PATH=/home/banksoal/app/venv/bin"
ExecStart=/home/banksoal/app/venv/bin/gunicorn \
          --config /home/banksoal/app/gunicorn_config.py \
          config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 10.3 Nginx Config

**/etc/nginx/sites-available/banksoal:**
```nginx
upstream banksoal_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name banksoal.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name banksoal.yourdomain.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/banksoal.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/banksoal.yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logs
    access_log /var/log/nginx/banksoal_access.log;
    error_log /var/log/nginx/banksoal_error.log;
    
    # Max upload size (for images)
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /home/banksoal/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/banksoal/app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://banksoal_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

---

## 11. Environment Variables

**.env.example:**
```bash
# Django
SECRET_KEY=your-secret-key-generate-with-python-secrets
DEBUG=False
ALLOWED_HOSTS=banksoal.yourdomain.com,www.banksoal.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=banksoal_db
DB_USER=banksoal
DB_PASSWORD=secure_db_password_here
DB_HOST=localhost
DB_PORT=5432

# Static & Media
STATIC_URL=/static/
STATIC_ROOT=/home/banksoal/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/home/banksoal/app/media

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis (optional)
REDIS_URL=redis://127.0.0.1:6379/0

# Logging
LOG_LEVEL=INFO
```

---

## 12. Dependencies

**requirements/base.txt:**
```
Django==5.0.1
psycopg2-binary==2.9.9
Pillow==10.1.0
python-decouple==3.8
django-extensions==3.2.3
django-crispy-forms==2.1
crispy-tailwind==1.0.3
```

**requirements/production.txt:**
```
-r base.txt
gunicorn==21.2.0
whitenoise==6.6.0
django-redis==5.4.0
celery==5.3.4
```

**requirements/development.txt:**
```
-r base.txt
django-debug-toolbar==4.2.0
pytest==7.4.3
pytest-django==4.7.0
black==23.12.1
flake8==6.1.0
isort==5.13.2
factory-boy==3.3.0
```

**package.json (for Tailwind):**
```json
{
  "name": "bank-soal-sd",
  "version": "1.0.0",
  "scripts": {
    "dev": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
  },
  "devDependencies": {
    "@tailwindcss/forms": "^0.5.7",
    "@tailwindcss/typography": "^0.5.10",
    "tailwindcss": "^3.4.0"
  }
}
```

---

**End of Technical Specification**
