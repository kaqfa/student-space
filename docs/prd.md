# Product Requirements Document (PRD)
## Bank Soal SD - Learning Management System

**Version:** 2.0  
**Last Updated:** 2025-01-11  
**Product Owner:** Fahri (Kaqfa)  
**Tech Lead:** Fahri  

---

## 1. Executive Summary

### 1.1 Product Vision
Aplikasi learning management system untuk membantu orang tua mengajarkan anak SD (kelas 3 dan 6) dengan bank soal terstruktur, progress tracking detail, dan analytics mendalam untuk mengidentifikasi kekuatan dan kelemahan pembelajaran.

### 1.2 Target Users
- **Primary:** Orang tua yang homeschooling anak SD
- **Secondary:** Anak SD kelas 3 dan 6 (sebagai end learners)
- **Supporting:** Pengajar/tutor (jika ada)

### 1.3 Core Value Proposition
- Progress tracking detail per kompetensi dan tag
- Advanced analytics untuk identifikasi learning gaps
- Quiz mode dengan timer untuk latihan terfokus
- Multi-role access (admin/pengajar/anak)
- Bulk import soal via JSON untuk efisiensi content creation

---

## 2. Problem Statement

### 2.1 Current Pain Points
1. **Lack of structured learning materials** - Tidak ada LKS untuk pedoman mengajar
2. **No progress visibility** - Sulit track perkembangan anak per topik
3. **Time constraints** - Orang tua sibuk, butuh sistem yang efisien
4. **No performance insights** - Tidak tau strengths/weaknesses anak di topik tertentu
5. **Manual assessment** - Semua tracking masih manual

### 2.2 Success Criteria
- Reduce time untuk prepare materi belajar (dari hours ke minutes)
- Clear visibility ke progress anak per kompetensi
- Data-driven insights untuk personalisasi pembelajaran
- Scalable content creation via bulk import

---

## 3. User Roles & Permissions

### 3.1 Admin (System Administrator)
**Capabilities:**
- Full CRUD pada semua data (subjects, topics, questions)
- Manage all users (parents, students)
- Bulk import questions via JSON
- View all analytics & reports
- Configure system settings
- Manage tags & kompetensi dasar

**Access Level:** Full system access

### 3.2 Parent (Orang Tua / Guru / Pengajar)
**Capabilities:**
- View & manage linked students (bisa punya lebih dari 1 student)
- Create/edit questions
- Assign quizzes to linked students
- **Proxy Quiz Mode:** Menjalankan kuis atas nama student (pilih student di awal sesi)
- View analytics for linked students
- Add learning notes/feedback
- Request link ke existing student (memerlukan verifikasi dari student)
- Create new student account (untuk anak kecil yang belum bisa self-register)

**Access Level:** Full access to linked students, read-only to public questions

### 3.3 Student (Siswa / Anak)
**Capabilities:**
- **Self-registration:** Bisa mendaftar sendiri tanpa parent
- Take quizzes (practice mode & timed mode) dari akun sendiri
- View own progress & analytics
- View question explanations
- Accept/reject link request dari parent
- Beraktivitas mandiri tanpa harus terhubung ke parent

**Access Level:** Full access to own data, execute quizzes

### 3.4 Student-Parent Relationship
**Linking Mechanism:**
- **Parent creates new student:** Parent bisa buat akun student baru (untuk anak kecil)
- **Link existing student:** Parent request link ke student yang sudah ada → Student harus verify/approve
- **Multiple parents:** Satu student bisa di-link ke multiple parents (misal: ayah & ibu, atau orang tua & guru les)
- **Independent student:** Student bisa aktif tanpa parent sama sekali

---

## 4. Core Features

### 4.1 Question Management

#### 4.1.1 Question Model
**Fields:**
- Question text (support markdown)
- Question type (pilgan, essay, isian)
- Subject & Topic
- Difficulty level (mudah, sedang, sulit)
- Answer options (for multiple choice)
- Correct answer
- Explanation (detailed solution)
- Tags (many-to-many) - for categorization
- Kompetensi Dasar (many-to-many) - curriculum mapping
- Image/diagram (optional)
- Has math formula (LaTeX support)
- Estimated time (seconds)
- Point value

#### 4.1.2 Tagging System
**Purpose:** Flexible categorization untuk advanced filtering & analytics

**Tag Categories:**
- **Skill Tags:** problem-solving, calculation, reading-comprehension, etc.
- **Topic Tags:** pecahan, geometri, tata-surya, etc.
- **Difficulty Tags:** basic, intermediate, advanced (berbeda dari difficulty level)
- **Custom Tags:** Bebas dibuat admin

**Use Cases:**
- Filter soal: "Semua soal tentang pecahan yang butuh problem-solving"
- Analytics: "Progress anak di skill reading-comprehension"
- Adaptive learning: "Kasih soal yang tagged 'visual-learner' untuk anak visual"

#### 4.1.3 Kompetensi Dasar (KD)
**Purpose:** Map soal ke kurikulum nasional

**Structure:**
- KD Code (e.g., 3.1, 4.2)
- KD Description
- Grade level
- Subject
- Many-to-many with Questions

**Use Cases:**
- Track progress per KD
- Generate report berbasis kurikulum
- Ensure curriculum coverage

#### 4.1.4 Bulk Import
**Format:** JSON
**Endpoint:** `/admin/questions/import/`

**JSON Structure:**
```json
{
  "questions": [
    {
      "subject": "Matematika",
      "topic": "Pecahan",
      "grade": 6,
      "question_text": "Hasil dari 1/2 + 1/4 = ...",
      "question_type": "pilgan",
      "difficulty": "mudah",
      "options": ["A. 1/2", "B. 3/4", "C. 1/4", "D. 1"],
      "answer_key": "B",
      "explanation": "1/2 + 1/4 = 2/4 + 1/4 = 3/4",
      "tags": ["operasi-hitung", "pecahan-sederhana"],
      "kompetensi_dasar": ["3.1"],
      "has_image": false,
      "has_math": true,
      "estimated_time": 60,
      "points": 10
    }
  ]
}
```

**Validation:**
- Subject & topic must exist (or create new)
- Tags auto-created if not exist
- KD must exist (error if not)
- Duplicate detection based on question_text hash

---

### 4.2 Progress Tracking

#### 4.2.1 Attempt Model
**Fields:**
- Student
- Question
- Quiz session (nullable - for practice mode)
- Answer given
- Is correct (boolean)
- Time taken (seconds)
- Timestamp
- Points earned

**Tracking Levels:**
1. **Per Question:** Individual question performance
2. **Per Topic:** Aggregate by topic
3. **Per Tag:** Aggregate by tag
4. **Per KD:** Aggregate by kompetensi dasar
5. **Per Difficulty:** Performance across difficulty levels

#### 4.2.2 Progress Metrics
**Calculated Metrics:**
- **Accuracy Rate:** (Correct / Total Attempts) × 100%
- **Average Time:** Mean time per question
- **Mastery Level:** Based on accuracy + attempts
  - Not Attempted (0 attempts)
  - Beginner (<50% accuracy)
  - Developing (50-74% accuracy)
  - Proficient (75-89% accuracy)
  - Mastered (≥90% accuracy)
- **Retention Rate:** Performance on repeated questions over time
- **Speed Efficiency:** (Estimated Time / Actual Time) × 100%

#### 4.2.3 Learning Analytics Dashboard

**Student View (Simplified):**
- Total questions attempted
- Overall accuracy
- Favorite topics (most attempted)
- Recent achievements
- Progress chart (timeline)

**Admin/Pengajar View (Detailed):**
- **Overview:**
  - Total questions attempted
  - Overall accuracy by subject
  - Time spent learning (total)
  - Questions mastered vs in-progress

- **Per Subject/Topic:**
  - Accuracy rate
  - Questions attempted vs available
  - Avg time per question
  - Mastery distribution

- **Per Tag:**
  - Skill performance heatmap
  - Strengths (high accuracy tags)
  - Weaknesses (low accuracy tags)
  - Recommended focus areas

- **Per KD:**
  - Curriculum coverage (% KD attempted)
  - KD mastery matrix
  - Gaps identification

- **Performance Trends:**
  - Accuracy over time (line chart)
  - Questions per day (bar chart)
  - Difficulty progression

- **Detailed Analytics:**
  - Question-level breakdown
  - Retry patterns (questions attempted multiple times)
  - Common mistakes (questions with low accuracy)
  - Time analysis (questions taking too long)

---

### 4.3 Quiz Mode

#### 4.3.1 Quiz Types

**Practice Mode:**
- No timer
- Immediate feedback after each question
- Can skip questions
- Show explanation immediately
- No scoring pressure

**Timed Quiz:**
- Countdown timer per question or whole quiz
- No immediate feedback
- Cannot skip (must answer or mark for review)
- Score shown at end
- Explanation available after completion

**Custom Quiz:**
- Admin/pengajar can create custom quiz
- Select specific questions or filters (by topic, tag, difficulty)
- Set time limit
- Assign to student(s)
- Set due date (optional)

#### 4.3.2 Quiz Session Model
**Fields:**
- Student
- Quiz type (practice, timed, custom)
- **Grade (kelas)** - untuk filter mata pelajaran yang tersedia di grade tersebut
- Questions (many-to-many through QuizQuestion)
- Start time
- End time (nullable - for in-progress)
- Time limit (seconds, nullable)
- Is completed
- Total score
- Max score
- Created by (parent for custom quiz or proxy mode)
- **Is proxy mode** (boolean) - apakah quiz dijalankan oleh parent atas nama student
- **Proxy user** (nullable FK to User) - parent yang menjalankan proxy quiz

#### 4.3.3 Quiz Settings
**Randomization:**
- Randomize question order (default: yes)
- Randomize answer options (default: yes)
- Pool random questions from filters (e.g., 10 random from topic X)

**Timer Options:**
- Per question timer (e.g., 60s per question)
- Total quiz timer (e.g., 30 min for 20 questions)
- No timer (practice mode)

**Feedback Options:**
- Immediate (after each question)
- End of quiz (after completion)
- Delayed (admin reviews first)

#### 4.3.4 Quiz Flow

**Starting Quiz:**
1. Select quiz type
2. Configure settings (if custom)
3. Review instructions
4. Start timer (if applicable)

**During Quiz:**
- Show question number (e.g., 5/20)
- Show remaining time (if timed)
- Mark for review option
- Previous/Next navigation (if allowed)
- Submit answer
- Auto-submit on timeout (if timed per question)

**Completing Quiz:**
- Review screen (show unanswered)
- Confirm submission
- Calculate score
- Record all attempts
- Show results page

**Results Page:**
- Total score
- Accuracy
- Time taken
- Per question review (correct/incorrect)
- Explanations
- Insights (strengths/weaknesses detected)

---

### 4.4 Student Management

#### 4.4.1 Student Model
**Fields:**
- Name
- Grade level (1-6)
- Date of birth (optional)
- Avatar (optional)
- Parent/guardian (FK to User, admin role)
- Assigned pengajar (many-to-many)
- Active status
- Notes (admin notes)

#### 4.4.2 Student Profile
**Sections:**
- Basic info
- Progress summary (across all subjects)
- Recent activity
- Assigned quizzes (upcoming & past)
- Performance highlights
- Learning preferences (visual, auditory, etc. - manual tags)

---

### 4.5 Reporting

#### 4.5.1 Report Types

**Progress Report:**
- Date range selector
- Subject/topic breakdown
- Questions attempted vs available
- Accuracy trends
- Mastery levels
- Time analysis
- Recommendations

**Performance Report:**
- Strengths & weaknesses matrix
- Tag-based skill analysis
- KD coverage & mastery
- Comparison to previous period
- Learning velocity (questions/week)

**Custom Report:**
- Admin-defined filters
- Export to PDF/CSV
- Scheduled reports (future enhancement)

#### 4.5.2 Export Options
- PDF (formatted, print-friendly)
- CSV (raw data for further analysis)
- Share link (read-only, expiring)

---

## 5. Technical Architecture

### 5.1 Tech Stack

**Backend:**
- Framework: Django 5.0
- Database: PostgreSQL 15+
- ORM: Django ORM
- API: Django REST Framework (optional, untuk future mobile app)
- Task Queue: Celery (optional, untuk heavy analytics)
- Cache: Redis (optional, untuk performance)

**Frontend:**
- Template Engine: Django Templates
- CSS Framework: Tailwind CSS 3.x
- JavaScript: HTMX (for dynamic interactions)
- Charts: Chart.js / Apache ECharts
- Math Rendering: KaTeX (lightweight) or MathJax

**Deployment:**
- App Server: Gunicorn
- Web Server: Nginx
- VPS: Domainesia atau similar
- OS: Ubuntu 22.04 LTS
- Process Manager: Systemd
- SSL: Let's Encrypt (Certbot)

**Database:**
- PostgreSQL on same VPS or separate (Supabase free tier as alternative)
- Backup: pg_dump automated daily

**Storage:**
- Media files: Local filesystem dengan Nginx serving
- Alternative: Cloudflare R2 / AWS S3 (future)

---

### 5.2 Database Schema (High-Level)

#### Core Tables

**users** (Django built-in, extended)
- id (PK)
- username
- email
- password (hashed)
- role (admin, pengajar, student)
- created_at
- updated_at

**students**
- id (PK)
- name
- grade
- date_of_birth
- avatar
- parent_id (FK → users, admin)
- created_at
- updated_at

**student_pengajar** (Many-to-Many)
- student_id (FK)
- pengajar_id (FK → users, pengajar role)

**subjects**
- id (PK)
- name
- grade
- order
- created_at

**topics**
- id (PK)
- subject_id (FK)
- name
- description
- order
- created_at

**kompetensi_dasar**
- id (PK)
- code (e.g., "3.1")
- description
- grade
- subject_id (FK)
- created_at

**tags**
- id (PK)
- name
- category (skill, topic, difficulty, custom)
- created_at

**questions**
- id (PK)
- topic_id (FK)
- question_text (TEXT)
- question_type (pilgan, essay, isian)
- difficulty (mudah, sedang, sulit)
- options (JSON for pilgan)
- answer_key (TEXT)
- explanation (TEXT)
- has_image (BOOLEAN)
- image_url (VARCHAR)
- has_math (BOOLEAN)
- estimated_time (INTEGER, seconds)
- points (INTEGER, default 10)
- order (INTEGER)
- created_by (FK → users)
- created_at
- updated_at

**question_tags** (Many-to-Many)
- question_id (FK)
- tag_id (FK)

**question_kd** (Many-to-Many)
- question_id (FK)
- kd_id (FK)

**quiz_sessions**
- id (PK)
- student_id (FK)
- quiz_type (practice, timed, custom)
- time_limit (INTEGER, nullable)
- start_time (TIMESTAMP)
- end_time (TIMESTAMP, nullable)
- is_completed (BOOLEAN)
- total_score (INTEGER)
- max_score (INTEGER)
- created_by (FK → users, for custom)
- created_at

**quiz_questions** (Many-to-Many with metadata)
- quiz_session_id (FK)
- question_id (FK)
- order (INTEGER)
- time_allocated (INTEGER, nullable)

**attempts**
- id (PK)
- student_id (FK)
- question_id (FK)
- quiz_session_id (FK, nullable)
- answer_given (TEXT)
- is_correct (BOOLEAN)
- time_taken (INTEGER, seconds)
- points_earned (INTEGER)
- created_at (TIMESTAMP)

**Indexes:**
- attempts: (student_id, question_id, created_at)
- attempts: (student_id, created_at)
- questions: (topic_id, difficulty)
- quiz_sessions: (student_id, is_completed)
- Full-text search on questions.question_text

---

### 5.3 Application Structure

```
bank_soal/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User management, authentication
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── admin.py
│   ├── students/          # Student management
│   │   ├── models.py
│   │   ├── views.py
│   │   └── admin.py
│   ├── subjects/          # Subjects & Topics
│   │   ├── models.py
│   │   ├── views.py
│   │   └── admin.py
│   ├── questions/         # Questions, Tags, KD
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   └── utils.py       # Import JSON utility
│   ├── quizzes/           # Quiz sessions & logic
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── quiz_engine.py # Quiz logic
│   ├── analytics/         # Progress tracking & reporting
│   │   ├── models.py      # Attempt model
│   │   ├── views.py
│   │   ├── reports.py     # Report generation
│   │   └── metrics.py     # Metrics calculation
│   └── core/              # Shared utilities
│       ├── mixins.py
│       ├── decorators.py
│       └── utils.py
├── templates/
│   ├── base.html
│   ├── components/        # Reusable HTMX components
│   ├── accounts/
│   ├── students/
│   ├── questions/
│   ├── quizzes/
│   └── analytics/
├── static/
│   ├── css/
│   │   └── styles.css     # Tailwind output
│   ├── js/
│   │   ├── htmx.min.js
│   │   └── app.js
│   └── images/
├── media/                 # Uploaded files (question images)
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── scripts/
    └── import_questions.py  # Bulk import script
```

---

### 5.4 Key Django Apps

#### 5.4.1 accounts
- Custom User model (extends AbstractUser)
- Role-based permissions
- Login/logout views
- Profile management

#### 5.4.2 students
- Student CRUD
- Student-pengajar assignment
- Student profile page

#### 5.4.3 subjects
- Subject & Topic CRUD
- Hierarchical display
- Django Admin customization

#### 5.4.4 questions
- Question CRUD
- Tag management
- KD management
- Bulk import via JSON (management command + admin action)
- Question search & filter

#### 5.4.5 quizzes
- Quiz creation & configuration
- Quiz session management
- Quiz-taking interface (HTMX-powered)
- Timer logic (JavaScript + HTMX)
- Answer validation & scoring

#### 5.4.6 analytics
- Attempt recording
- Metrics calculation (cached)
- Progress dashboard
- Report generation
- Data visualization (Chart.js integration)

---

### 5.5 Security Considerations

**Authentication:**
- Django built-in auth
- Password hashing (bcrypt)
- Session management
- CSRF protection

**Authorization:**
- Role-based access control (RBAC)
- Django permissions & groups
- Custom decorators (@admin_required, @pengajar_or_admin_required)
- Object-level permissions (student can only view own data)

**Data Protection:**
- SQL injection prevention (Django ORM)
- XSS prevention (template auto-escaping)
- HTTPS only (production)
- Secure headers (django-csp, django-security)

**File Upload:**
- Whitelist extensions (jpg, png, svg)
- Max file size limit (5MB)
- Virus scanning (future: ClamAV)

---

## 6. User Flows

### 6.1 Admin Flow: Bulk Import Questions

1. Login as admin
2. Navigate to `/admin/questions/import/`
3. Upload JSON file or paste JSON
4. Preview imported questions (validation)
5. Confirm import
6. System creates:
   - Questions
   - Auto-creates tags if not exist
   - Links to existing KD
   - Creates subjects/topics if needed
7. Show summary: "50 questions imported, 5 tags created"
8. Redirect to question list

### 6.2 Student Flow: Take Timed Quiz

1. Login as student
2. Dashboard shows available quizzes
3. Click "Start Quiz: Matematika - Pecahan"
4. Quiz config: 10 questions, 10 min total
5. Click "Start"
6. Question 1 appears, timer starts (10:00)
7. Select answer, click "Next"
8. Question 2 appears (timer continues: 9:45)
9. ... repeat for all 10 questions
10. Review screen (show unanswered if any)
11. Click "Submit Quiz"
12. Timer stops, calculate score
13. Results page:
    - Score: 8/10 (80%)
    - Time: 7:32
    - Per question breakdown (✓/✗)
    - Explanations for incorrect
    - Insights: "Strong in pecahan sederhana, needs work on campuran"

### 6.3 Admin Flow: View Student Analytics

1. Login as admin
2. Navigate to Students list
3. Click on "Anak Pertama (Kelas 6)"
4. Student profile page loads
5. Tabs: Overview | Progress | Analytics | Quizzes
6. Click "Analytics"
7. Dashboard shows:
   - **Subject Performance** (pie chart: Math 85%, IPA 78%, etc)
   - **Tag Heatmap** (skill matrix)
   - **KD Coverage** (3.1: Mastered, 3.2: Proficient, 3.3: Not Attempted)
   - **Accuracy Trend** (line chart over last 30 days)
   - **Time Analysis** (avg time per difficulty level)
8. Filter by date range: "Last 7 days"
9. Export to PDF

### 6.4 Pengajar Flow: Create Custom Quiz

1. Login as pengajar
2. Navigate to Quizzes > Create Custom Quiz
3. Form:
   - Select student(s): [Anak Pertama]
   - Quiz name: "Latihan Pecahan Minggu Ini"
   - Filters:
     - Subject: Matematika
     - Topic: Pecahan
     - Tags: operasi-hitung, pecahan-campuran
     - Difficulty: sedang, sulit
     - Question count: 15 (random from pool)
   - Settings:
     - Time limit: 20 minutes
     - Randomize: Yes
     - Feedback: End of quiz
   - Due date: 2025-01-15
4. Preview questions (optional)
5. Click "Create & Assign"
6. Student receives notification (if implemented)
7. Quiz appears in student's dashboard

---

## 7. UI/UX Requirements

### 7.1 Design Principles
- **Clean & Minimal:** Fokus pada content, minimal distraction
- **Responsive:** Mobile-first (anak mungkin pake tablet)
- **Accessible:** WCAG AA compliance (contrast, font size)
- **Fast:** HTMX untuk dynamic tanpa full page reload

### 7.2 Color Scheme
- **Primary:** Blue (#3B82F6) - trust, calm
- **Success:** Green (#10B981) - correct answers
- **Warning:** Orange (#F59E0B) - medium difficulty
- **Danger:** Red (#EF4444) - hard difficulty, incorrect
- **Neutral:** Gray shades (#F3F4F6, #E5E7EB)

### 7.3 Typography
- **Headings:** Inter (clean, modern)
- **Body:** System fonts (fast load)
- **Question text:** 18px, line-height 1.6 (readability)
- **Code/Math:** JetBrains Mono atau Fira Code

### 7.4 Key Pages Layout

#### Dashboard (Student)
```
+----------------------------------+
| Header: Logo | Hi, Anak! | Logout|
+----------------------------------+
| Sidebar       | Main Content     |
| - Dashboard   | +---------------+|
| - Practice    | | Quick Stats   ||
| - Quizzes     | | - 45 Q done   ||
| - Progress    | | - 82% avg     ||
|               | +---------------+|
|               | Recent Activity  |
|               | +---------------+|
|               | | Math: 5/5 ✓  ||
|               | | IPA: 3/5     ||
|               | +---------------+|
|               | Upcoming Quizzes |
+----------------------------------+
```

#### Quiz Interface
```
+----------------------------------+
| Quiz: Pecahan | Q 5/10 | ⏱ 08:32|
+----------------------------------+
| Question Text (large, clear)     |
| Hasil dari 1/2 + 3/4 = ...       |
|                                  |
| [ ] A. 1/4                       |
| [x] B. 5/4                       |
| [ ] C. 4/5                       |
| [ ] D. 3/2                       |
|                                  |
| [Mark for Review] [Next →]      |
+----------------------------------+
```

#### Analytics Dashboard (Admin)
```
+----------------------------------+
| Student: Anak Pertama (Grade 6) |
+----------------------------------+
| [Overview][Progress][Analytics]  |
+----------------------------------+
| Date Range: [Last 30 Days ▼]     |
|                                  |
| +--------------+--------------+  |
| | Subject Perf | Tag Heatmap  |  |
| | (Pie Chart)  | (Matrix)     |  |
| +--------------+--------------+  |
|                                  |
| KD Coverage Progress             |
| +------------------------------+ |
| | 3.1 ████████░░ 80% Proficient| |
| | 3.2 ██████████ 95% Mastered  | |
| +------------------------------+ |
|                                  |
| [Export PDF] [Export CSV]        |
+----------------------------------+
```

### 7.5 Design Standards (Referensi: Spike Admin)

**Design Reference:** [Spike Admin React Tailwind](https://spike-react-tailwind-main.netlify.app/)

#### 7.5.1 Layout Structure

**Overall Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        TOP NAVBAR                                │
│  [Logo] [Search]                   [Theme] [Notif] [User Avatar]│
├────────────────┬────────────────────────────────────────────────┤
│                │                                                 │
│   SIDEBAR      │              MAIN CONTENT AREA                 │
│   (~250px)     │                                                 │
│                │   ┌─────────────────────────────────┐          │
│  - Dashboard   │   │ Page Header                     │          │
│  - Siswa       │   │ [Title] [Breadcrumb]  [Actions] │          │
│  - Soal        │   └─────────────────────────────────┘          │
│  - Kuis        │                                                 │
│  - Mapel       │   ┌─────────────────────────────────┐          │
│                │   │     CONTENT CARDS               │          │
│                │   └─────────────────────────────────┘          │
│                │                                                 │
└────────────────┴────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Fixed sidebar (250px width) - collapsible on mobile
- Top navbar dengan search, theme toggle, notifications, user menu
- Main content area dengan generous padding
- Card-based content containers

#### 7.5.2 Color Palette (Refined)

| Role | Warna | Hex Code | Tailwind Class |
|------|-------|----------|----------------|
| **Primary** | Blue | #5D87FF | `bg-blue-500` / custom |
| **Background** | Light Gray | #F4F7FB | `bg-gray-50` / `bg-slate-50` |
| **Card** | White | #FFFFFF | `bg-white` |
| **Success** | Green | #13DEB9 | `bg-green-100 text-green-700` |
| **Warning** | Orange | #FFAE1F | `bg-amber-100 text-amber-700` |
| **Danger** | Red | #FA896B | `bg-red-100 text-red-700` |
| **Text Primary** | Dark Gray | #2A3547 | `text-gray-900` |
| **Text Secondary** | Medium Gray | #5A6A85 | `text-gray-500` |

#### 7.5.3 Component Standards

**Card Component:**
- Border radius: `rounded-xl` (large, modern feel)
- Shadow: `shadow-sm` (subtle, clean)
- Padding: `p-6` internal padding
- Border: Optional `border border-gray-100`

**Button Hierarchy:**
- **Primary:** Solid blue (`bg-blue-600 text-white`)
- **Secondary:** Outline (`border border-gray-300 text-gray-700`)
- **Danger:** Red for destructive actions
- **Ghost:** Transparent with text color only

**Status Badges (Pill-shaped):**
- Success: `bg-green-100 text-green-800 rounded-full px-2.5 py-0.5`
- Warning: `bg-amber-100 text-amber-800 rounded-full px-2.5 py-0.5`
- Danger: `bg-red-100 text-red-800 rounded-full px-2.5 py-0.5`
- Info: `bg-blue-100 text-blue-800 rounded-full px-2.5 py-0.5`

#### 7.5.4 Page Layout Patterns

**List Page (Table View):**
```
┌─────────────────────────────────────────────────────┐
│ Page Header: [Title]           [+ Tambah] [Filter]  │
├─────────────────────────────────────────────────────┤
│ Filter Section (collapsible, optional)              │
├─────────────────────────────────────────────────────┤
│ TABLE                                               │
│ ┌───────────────────────────────────────────────┐  │
│ │ [✓] │ Nama     │ Status  │ Tanggal │ Aksi    │  │
│ ├───────────────────────────────────────────────┤  │
│ │ [ ] │ Data 1   │ [Badge] │ dd/mm   │ [•••]   │  │
│ └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│ Pagination: [Prev] Page 1 of 5 [Next]              │
└─────────────────────────────────────────────────────┘
```

**Form Page (Create/Edit):**
```
┌─────────────────────────────────────────────────────┐
│ Page Header: [← Back] Form Title                    │
├───────────────────────────────┬─────────────────────┤
│   MAIN FORM (2/3 width)       │ SIDEBAR INFO (1/3)  │
│   ┌─────────────────────┐     │ ┌─────────────────┐ │
│   │ General Info        │     │ │ Status          │ │
│   │ - Field 1           │     │ │ [Select]        │ │
│   │ - Field 2           │     │ │                 │ │
│   └─────────────────────┘     │ │ [Save] [Cancel] │ │
│   ┌─────────────────────┐     │ └─────────────────┘ │
│   │ Additional Info     │     │                     │
│   └─────────────────────┘     │                     │
└───────────────────────────────┴─────────────────────┘
```

**Detail Page:**
```
┌─────────────────────────────────────────────────────┐
│ Page Header: [← Back] Detail Title    [Edit][Delete]│
├───────────────────────────────┬─────────────────────┤
│   MAIN CONTENT (2/3)          │ SIDEBAR (1/3)       │
│   ┌─────────────────────┐     │ ┌─────────────────┐ │
│   │ Content Detail      │     │ │ Quick Info      │ │
│   │ - Field: Value      │     │ │ - Status        │ │
│   └─────────────────────┘     │ │ - Created       │ │
│   ┌─────────────────────┐     │ └─────────────────┘ │
│   │ Related Items       │     │                     │
│   └─────────────────────┘     │                     │
└───────────────────────────────┴─────────────────────┘
```

#### 7.5.5 Reusable Template Components

**Required Partials:**
- `templates/partials/card.html` - Base card container
- `templates/partials/page_header.html` - Page title + actions
- `templates/partials/badge.html` - Status badges
- `templates/partials/data_table.html` - Standardized table
- `templates/partials/form_section.html` - Form grouping
- `templates/partials/empty_state.html` - Empty data message
- `templates/partials/pagination.html` - Consistent pagination

**Required Layouts:**
- `templates/layouts/base_admin.html` - Sidebar + navbar layout
- `templates/layouts/base_public.html` - Public pages (login, register)

---

## 8. Deployment Plan

### 8.1 VPS Requirements
- **CPU:** 2 cores minimum
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 20GB SSD minimum
- **OS:** Ubuntu 22.04 LTS
- **Network:** 100Mbps+

### 8.2 Deployment Steps

#### Initial Setup
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib nginx supervisor \
  certbot python3-certbot-nginx git

# 3. PostgreSQL setup
sudo -u postgres createuser banksoal
sudo -u postgres createdb banksoal_db
sudo -u postgres psql
# ALTER USER banksoal WITH PASSWORD 'secure_password';
# GRANT ALL PRIVILEGES ON DATABASE banksoal_db TO banksoal;

# 4. Create project user
sudo adduser banksoal
sudo usermod -aG sudo banksoal

# 5. Clone repository
su - banksoal
git clone <repo-url> /home/banksoal/app
cd /home/banksoal/app

# 6. Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt

# 7. Environment variables
cp .env.example .env
nano .env  # Edit with production values

# 8. Django setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 9. Gunicorn systemd service
sudo nano /etc/systemd/system/banksoal.service
# (copy config from docs)
sudo systemctl enable banksoal
sudo systemctl start banksoal

# 10. Nginx configuration
sudo nano /etc/nginx/sites-available/banksoal
# (copy config from docs)
sudo ln -s /etc/nginx/sites-available/banksoal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. SSL
sudo certbot --nginx -d banksoal.yourdomain.com

# 12. Firewall
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### Environment Variables (.env)
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=banksoal.yourdomain.com

# Database
DB_NAME=banksoal_db
DB_USER=banksoal
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Static & Media
STATIC_ROOT=/home/banksoal/app/staticfiles
MEDIA_ROOT=/home/banksoal/app/media

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 8.3 Backup Strategy

**Database Backup (Daily):**
```bash
# Cron job: /etc/cron.daily/backup-db
#!/bin/bash
pg_dump -U banksoal banksoal_db | gzip > /home/banksoal/backups/db-$(date +%Y%m%d).sql.gz
# Keep last 30 days
find /home/banksoal/backups -name "db-*.sql.gz" -mtime +30 -delete
```

**Media Backup (Weekly):**
```bash
# Cron job: /etc/cron.weekly/backup-media
#!/bin/bash
tar -czf /home/banksoal/backups/media-$(date +%Y%m%d).tar.gz /home/banksoal/app/media
```

**Offsite Backup:**
- Sync to cloud storage (Google Drive, Dropbox, AWS S3)
- Use rclone for automation

### 8.4 Monitoring

**Application Monitoring:**
- Django logging to file
- Error notifications via email
- Uptime monitoring (UptimeRobot, Pingdom)

**Server Monitoring:**
- Disk space: `df -h`
- Memory: `free -h`
- CPU: `htop`
- Logs: `/var/log/nginx/`, Django logs

**Performance:**
- Django Debug Toolbar (development only)
- PostgreSQL query analysis (pg_stat_statements)
- Nginx access logs analysis

---

## 9. Development Phases

### Phase 0: Setup & Infrastructure (Week 1)
- [ ] Setup VPS
- [ ] Install PostgreSQL
- [ ] Setup Django project structure
- [ ] Configure Tailwind CSS + HTMX
- [ ] Setup Git repository
- [ ] Create base templates
- [ ] Configure Django Admin

**Deliverable:** Working Django app with auth

---

### Phase 1: Core Data Models (Week 1-2)
- [ ] User model & roles (admin, pengajar, student)
- [ ] Student model
- [ ] Subject & Topic models
- [ ] Kompetensi Dasar model
- [ ] Tag model
- [ ] Question model (with many-to-many relations)
- [ ] Migrations
- [ ] Django Admin for all models
- [ ] Seed data (subjects, topics for kelas 3 & 6)

**Deliverable:** Complete database schema with admin interface

---

### Phase 2: Question Management (Week 2-3)
- [ ] Question CRUD views
- [ ] Tag management interface
- [ ] KD management interface
- [ ] Question list with filters (subject, topic, difficulty, tags)
- [ ] Question detail view
- [ ] Bulk import JSON functionality
  - [ ] Management command: `python manage.py import_questions data.json`
  - [ ] Admin action: Upload JSON via admin panel
  - [ ] Validation & error handling
- [ ] Image upload for questions

**Deliverable:** Full question management system with bulk import

---

### Phase 3: Student Management (Week 3)
- [ ] Student CRUD views
- [ ] Student profile page
- [ ] Assign pengajar to student
- [ ] Student list for admin/pengajar
- [ ] Basic student dashboard

**Deliverable:** Student management system

---

### Phase 4: Quiz Engine (Week 4-5)
- [ ] Quiz session model & logic
- [ ] Practice mode
  - [ ] Browse questions by topic
  - [ ] Answer questions
  - [ ] Immediate feedback
  - [ ] Show explanation
- [ ] Timed quiz mode
  - [ ] Quiz configuration (filters, time limit)
  - [ ] Timer implementation (JavaScript)
  - [ ] Question navigation
  - [ ] Auto-submit on timeout
  - [ ] Results page with breakdown
- [ ] Custom quiz creation (admin/pengajar)
  - [ ] Create quiz form
  - [ ] Assign to students
  - [ ] Question pool selection
- [ ] Quiz session persistence (can pause/resume)

**Deliverable:** Fully functional quiz system

---

### Phase 5: Progress Tracking & Analytics (Week 5-6)
- [ ] Attempt model & recording
- [ ] Basic progress metrics calculation
  - [ ] Accuracy per subject/topic
  - [ ] Questions attempted
  - [ ] Mastery levels
- [ ] Student progress dashboard
  - [ ] Overview stats
  - [ ] Recent activity
  - [ ] Progress charts (Chart.js)
- [ ] Admin analytics dashboard
  - [ ] Subject performance
  - [ ] Tag-based analytics (skill heatmap)
  - [ ] KD coverage matrix
  - [ ] Accuracy trends over time
  - [ ] Time analysis
  - [ ] Detailed question-level breakdown
- [ ] Performance reports
  - [ ] Generate PDF reports
  - [ ] Export CSV data

**Deliverable:** Complete analytics & reporting system

---

### Phase 6: UI/UX Polish (Week 7)
- [ ] Responsive design refinement
- [ ] HTMX interactions polish
- [ ] Loading states & animations
- [ ] Error handling & user feedback
- [ ] Print stylesheets (for reports)
- [ ] Accessibility improvements
- [ ] Math formula rendering (KaTeX)
- [ ] Image optimization

**Deliverable:** Production-ready UI/UX

---

### Phase 7: Testing & Deployment (Week 7-8)
- [ ] Unit tests for models
- [ ] Integration tests for views
- [ ] Quiz engine testing (edge cases)
- [ ] Analytics calculation verification
- [ ] Import JSON validation tests
- [ ] Performance testing (large datasets)
- [ ] Security audit
- [ ] VPS deployment
- [ ] SSL setup
- [ ] Backup configuration
- [ ] Monitoring setup
- [ ] Documentation (user guide)

**Deliverable:** Production deployment

---

### Phase 8: Content Creation (Ongoing)
- [ ] Generate initial question set (100+ questions)
  - [ ] Matematika kelas 6 (30 questions)
  - [ ] Matematika kelas 3 (30 questions)
  - [ ] IPA kelas 6 (20 questions)
  - [ ] IPA kelas 3 (20 questions)
- [ ] Create tags library
- [ ] Map questions to KD
- [ ] Create sample quizzes

**Deliverable:** Content-ready platform

---

## 10. Success Metrics (Post-Launch)

### 10.1 User Engagement
- **Daily Active Students:** Anak login dan attempt minimal 1 question/day
- **Questions per Session:** Average 10+ questions per study session
- **Quiz Completion Rate:** >80% of started quizzes completed
- **Return Rate:** Student return next day after using (retention)

### 10.2 Learning Effectiveness
- **Accuracy Improvement:** Trend naik over time per topic
- **Mastery Achievement:** Berapa banyak topics yang reached "Mastered" status
- **Time Efficiency:** Average time per question menurun (semakin cepat & confident)
- **Retention:** Repeated questions show consistent or improved accuracy

### 10.3 System Usage
- **Admin Time Saved:** Berapa lama untuk prepare 1 session (target: <10 min)
- **Content Growth:** Questions added per week via bulk import
- **Analytics Access:** Frequency admin checks progress dashboard
- **Report Generation:** Reports generated per month

### 10.4 Technical Performance
- **Page Load Time:** <2s for all pages
- **Quiz Responsiveness:** <100ms answer submission
- **Uptime:** >99.5%
- **Database Query Time:** <50ms average

---

## 11. Future Enhancements (Phase 2+)

### 11.1 Adaptive Learning (Priority: High)
- AI-powered question recommendation based on performance
- Dynamic difficulty adjustment
- Spaced repetition scheduling (algorithm untuk kapan repeat question)
- Learning path generation (personalized curriculum)

### 11.2 Gamification (Priority: Medium)
- Achievement badges (10 questions done, 100% accuracy, etc)
- Leaderboard (optional, jika ada competitive aspect)
- Daily streaks
- Point system dengan rewards

### 11.3 Collaboration (Priority: Medium)
- Discussion forum per question (student ask, pengajar/admin answer)
- Peer review (students can suggest questions - admin approves)
- Group quizzes (multiple students take same quiz)
- Study groups

### 11.4 Content Enhancement (Priority: Medium)
- Video explanations embed (YouTube links)
- Interactive diagrams (JavaScript-based)
- Audio questions (listening comprehension)
- AR/VR content (very future)

### 11.5 Mobile App (Priority: Low)
- React Native atau Flutter app
- Offline mode (download questions for practice)
- Push notifications (quiz reminders)
- Camera untuk scan written answers (essay auto-check via OCR + AI)

### 11.6 Integration (Priority: Low)
- Google Classroom sync
- Zoom/Meet integration (virtual teaching)
- Calendar integration (schedule study sessions)
- Third-party curriculum platforms

### 11.7 AI Features (Priority: High - Long Term)
- Auto-generate questions from topic description (GPT-4)
- Auto-grade essay answers (semantic analysis)
- Personalized feedback generation
- Learning gap analysis & recommendation

---

## 12. Risk Assessment

### 12.1 Technical Risks

**Risk: VPS Downtime**
- **Mitigation:** Monitoring + automated restart, backup VPS ready
- **Probability:** Low
- **Impact:** High

**Risk: Database Corruption**
- **Mitigation:** Daily backups, replication (future)
- **Probability:** Very Low
- **Impact:** Critical

**Risk: Performance Issues (Large Dataset)**
- **Mitigation:** Database indexing, query optimization, caching (Redis)
- **Probability:** Medium
- **Impact:** Medium

**Risk: Security Breach**
- **Mitigation:** Regular updates, security audit, HTTPS, strong passwords
- **Probability:** Low
- **Impact:** High

### 12.2 User Adoption Risks

**Risk: Too Complex for Kids**
- **Mitigation:** Simple student interface, onboarding guide, parent supervision mode
- **Probability:** Low
- **Impact:** Medium

**Risk: Low Engagement (Boring)**
- **Mitigation:** Gamification, varied content, immediate feedback
- **Probability:** Medium
- **Impact:** High

**Risk: Content Quality Issues**
- **Mitigation:** Admin review before publish, versioning, feedback mechanism
- **Probability:** Low
- **Impact:** Medium

### 12.3 Development Risks

**Risk: Scope Creep**
- **Mitigation:** Strict phase planning, MVP focus, feature freeze periods
- **Probability:** Medium
- **Impact:** High

**Risk: Timeline Delays**
- **Mitigation:** Buffer time, prioritization, agile iterations
- **Probability:** Medium
- **Impact:** Medium

**Risk: Solo Development Bottleneck**
- **Mitigation:** Clear documentation, modular code, AI assistance (Claude Code)
- **Probability:** High
- **Impact:** Medium

---

## 13. Appendix

### 13.1 Glossary

- **KD (Kompetensi Dasar):** Basic competencies from national curriculum
- **Quiz Session:** A single instance of taking a quiz
- **Attempt:** A student's answer to a specific question
- **Mastery Level:** Calculated metric of student proficiency on a topic
- **Tag:** Flexible categorization label for questions
- **HTMX:** JavaScript library for dynamic HTML without writing JavaScript
- **ORM:** Object-Relational Mapping (Django ORM)

### 13.2 References

- Django Documentation: https://docs.djangoproject.com/
- HTMX Documentation: https://htmx.org/
- Tailwind CSS: https://tailwindcss.com/
- PostgreSQL: https://www.postgresql.org/docs/
- Chart.js: https://www.chartjs.org/

### 13.3 Contact & Stakeholders

- **Product Owner:** Fahri
- **Tech Lead:** Fahri
- **QA/Tester:** Istri (co-teacher feedback)
- **End Users:** 2 anak (kelas 3 & 6)

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2025-01-11 | Fahri | Complete rewrite for Django + PostgreSQL architecture |
| 1.0 | 2025-01-11 | Fahri | Initial draft (Next.js + Firestore) - deprecated |

---

**End of PRD**
