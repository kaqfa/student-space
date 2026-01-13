# TODO List - Bank Soal SD (Django + PostgreSQL)

## Phase 0: Environment Setup (Day 1)

### Local Development Setup
- [x] Install Python 3.11+
  ```bash
  python3.11 --version
  ```
- [x] Install PostgreSQL 15+
  ```bash
  psql --version
  ```
- [x] Install Node.js (untuk Tailwind)
  ```bash
  node --version
  npm --version
  ```
- [x] Create project directory
  ```bash
  mkdir bank_soal_project
  cd bank_soal_project
  ```
- [x] Initialize Git repository
  ```bash
  git init
  git remote add origin <your-repo-url>
  ```

### PostgreSQL Setup (Local)
- [x] Create database
  ```bash
  sudo -u postgres psql
  CREATE DATABASE banksoal_dev;
  CREATE USER banksoal WITH PASSWORD 'dev_password';
  GRANT ALL PRIVILEGES ON DATABASE banksoal_dev TO banksoal;
  \q
  ```
- [x] Test connection
  ```bash
  psql -U banksoal -d banksoal_dev -h localhost
  ```

### Django Project Initialization
- [x] Create virtual environment
  ```bash
  python3.11 -m venv venv
  source venv/bin/activate  # Linux/Mac
  # venv\Scripts\activate  # Windows
  ```
- [x] Install Django
  ```bash
  pip install Django==5.0.1
  ```
- [x] Create Django project
  ```bash
  django-admin startproject config .
  ```
- [x] Install initial dependencies
  ```bash
  mkdir requirements
  # Create requirements/base.txt (copy from spec)
  pip install -r requirements/base.txt
  ```
- [x] Create .env file
  ```bash
  cp .env.example .env
  # Edit .env dengan credentials lokal
  ```
- [x] Configure settings structure
  ```bash
  mkdir -p config/settings
  # Create base.py, development.py, production.py
  ```
- [x] Test runserver
  ```bash
  python manage.py runserver
  # Visit http://localhost:8000
  ```

### Tailwind CSS Setup
- [x] Initialize npm
  ```bash
  npm init -y
  ```
- [x] Install Tailwind
  ```bash
  npm install -D tailwindcss @tailwindcss/forms @tailwindcss/typography
  npx tailwindcss init
  ```
- [x] Create static/css/input.css
- [x] Configure tailwind.config.js (copy from spec)
- [x] Build CSS
  ```bash
  npm run build
  ```
- [x] Test in template

---

## Phase 1: Core Models & Admin (Day 2-3)

### Create Django Apps
- [x] Create apps directory
  ```bash
  mkdir apps
  touch apps/__init__.py
  ```
- [x] Create accounts app
  ```bash
  python manage.py startapp accounts apps/accounts
  ```
- [x] Create students app
  ```bash
  python manage.py startapp students apps/students
  ```
- [x] Create subjects app
  ```bash
  python manage.py startapp subjects apps/subjects
  ```
- [x] Create questions app
  ```bash
  python manage.py startapp questions apps/questions
  ```
- [x] Create quizzes app
  ```bash
  python manage.py startapp quizzes apps/quizzes
  ```
- [x] Create analytics app
  ```bash
  python manage.py startapp analytics apps/analytics
  ```
- [x] Create core app (utilities)
  ```bash
  python manage.py startapp core apps/core
  ```
- [x] Register all apps in settings.INSTALLED_APPS

### accounts App
- [x] Create custom User model (extend AbstractUser)
  - [x] Add role field (admin, parent, student) - UPDATED from pengajar
  - [x] Add avatar field
  - [x] Add phone field
  - [x] Add grade field (for students only) ✅ DONE
  - [x] Add date_of_birth field (for students only) ✅ DONE
- [x] Update AUTH_USER_MODEL in settings
- [x] Create ParentStudent linking model ✅ DONE
  - [x] parent FK, student FK, status (pending/approved/rejected)
  - [x] created_by_parent boolean
  - [x] verified_at timestamp
  - [x] approve() and reject() methods
- [x] Create UserAdmin
- [x] Create ParentStudentAdmin ✅ DONE
- [x] Create migrations
- [x] Run migrations
- [x] Create superuser
  ```bash
  python manage.py createsuperuser
  ```
- [x] Test admin login

### students App (Now: Parent-Student Management)
- [x] **ARCHITECTURE CHANGE**: Student is now a User with role='student' ✅ DONE
  - [x] Deprecate separate Student model (kept for migration)
  - [x] Use User model with role='student' directly
  - [x] Parent-student relationship via ParentStudent model
- [x] Update decorators (pengajar → parent) ✅ DONE
- [x] Update mixins (PengajarOrAdminMixin → ParentOrAdminMixin) ✅ DONE
- [x] Create migrations for architecture change ✅ DONE
- [x] Run migrations ✅ DONE
- [ ] Update StudentAdmin to show students (users with role='student')
- [ ] Test CRUD in admin

### subjects App
- [x] Create Subject model
  - [x] name, grade, order
  - [x] icon, color
  - [x] created_at
- [x] Create Topic model
  - [x] subject FK
  - [x] name, description, order
  - [x] timestamps
- [x] Create SubjectAdmin (with inline topics)
- [x] Create TopicAdmin
- [x] Create migrations
- [x] Run migrations
- [x] Seed initial subjects (management command)
  ```bash
  python manage.py seed_subjects
  ```

### questions App
- [x] Create KompetensiDasar model
  - [x] code, description
  - [x] grade, subject FK
  - [x] created_at
- [x] Create Tag model
  - [x] name, category
  - [x] description, created_at
- [x] Create Question model (complex!)
  - [x] topic FK
  - [x] question_text, question_type, difficulty
  - [x] options (JSON), answer_key, explanation
  - [x] has_image, image, has_math
  - [x] estimated_time, points, order
  - [x] tags M2M, kompetensi_dasar M2M
  - [x] created_by FK, timestamps
- [x] Create QuestionAdmin (advanced filters)
- [x] Create TagAdmin
- [x] Create KDAdmin
- [x] Create migrations
- [x] Run migrations
- [x] Test question creation in admin

### quizzes App
- [x] Create QuizSession model
  - [x] student FK, quiz_type
  - [x] title, time_limit
  - [x] start_time, end_time
  - [x] is_completed
  - [x] total_score, max_score
  - [x] created_by FK, due_date
  - [x] created_at
- [x] Create QuizQuestion model (through table)
  - [x] quiz_session FK, question FK
  - [x] order, time_allocated
- [x] Create QuizSessionAdmin
- [x] Create migrations
- [x] Run migrations

### analytics App
- [x] Create Attempt model
  - [x] student FK, question FK, quiz_session FK
  - [x] answer_given, is_correct
  - [x] time_taken, points_earned
  - [x] created_at
- [x] Implement save() method (auto-calculate points)
- [x] Create AttemptAdmin
- [x] Create migrations
- [x] Run migrations
- [x] Test attempt creation

---

## Phase 2: Base Templates & Authentication (Day 3-4)

### Template Structure
- [x] Create templates directory
- [x] Create base.html
  - [x] Include Tailwind CSS
  - [x] Include HTMX
  - [x] Include Chart.js
  - [x] Include KaTeX
  - [x] Block structure (title, content, extra_css, extra_js)
- [x] Create components directory
  - [x] navbar.html
  - [x] sidebar.html
  - [x] footer.html
  - [x] alerts.html
  - [x] pagination.html
- [x] Create partials directory (for HTMX)
- [x] Create errors directory (404, 500, 403)

### accounts Views & URLs
- [x] LoginView (using Django auth)
  - [x] Template: accounts/login.html
  - [x] Form: LoginForm
- [x] LogoutView
- [x] ProfileView
  - [x] Template: accounts/profile.html
  - [x] Form: UserUpdateForm
- [x] PasswordChangeView
- [x] Create accounts/urls.py
- [x] Include in main urls.py
- [x] Create decorators:
  - [x] @admin_required
  - [x] @parent_required - NEW ✅ DONE
  - [x] @parent_or_admin_required - RENAME from pengajar_or_admin_required ✅ DONE
  - [x] @student_required - RENAME from student_only ✅ DONE
- [x] Create mixins:
  - [x] AdminRequiredMixin
  - [x] ParentRequiredMixin - NEW ✅ DONE
  - [x] ParentOrAdminMixin - RENAME from PengajarOrAdminMixin ✅ DONE
  - [x] StudentRequiredMixin - RENAME from StudentOnlyMixin ✅ DONE
- [x] Test login/logout flow

### Static Files
- [x] Configure STATIC_URL, STATIC_ROOT
- [x] Configure STATICFILES_DIRS
- [x] Create static/css/input.css (Tailwind source)
- [x] Create static/js/app.js (custom JS)
- [x] Download HTMX to static/js/htmx.min.js
- [x] Download Chart.js to static/js/chart.js
- [x] Download KaTeX to static/js/ and static/css/
- [x] Run collectstatic (test)
  ```bash
  python manage.py collectstatic
  ```

### Media Files
- [x] Configure MEDIA_URL, MEDIA_ROOT
- [x] Add media URL pattern (development)
- [x] Create media/questions/images/ directory
- [x] Test image upload

---

## Phase 3: Question Management (Day 5-6)

### questions Views
- [x] QuestionListView
  - [x] Template: questions/list.html
  - [x] Filter form (subject, topic, difficulty, tags)
  - [x] Pagination (20 per page)
  - [x] HTMX filtering (not implemented yet, basic GET filters used)
- [x] QuestionDetailView
  - [x] Template: questions/detail.html
  - [x] Show all question data
  - [x] Render LaTeX (if has_math)
  - [x] Show image (if has_image)
- [x] QuestionCreateView (admin/pengajar only)
  - [x] Template: questions/form.html
  - [x] Form: QuestionForm
  - [x] Tag selection (multiple)
  - [x] KD selection (multiple)
- [x] QuestionUpdateView (admin/pengajar only)
- [x] QuestionDeleteView (admin only)
- [x] Create questions/urls.py
- [x] Include in main urls.py
- [x] Test CRUD flow

### Tag & KD Management
- [x] TagListView
  - [x] Template: questions/tag_list.html
  - [x] Group by category (Not implemented, simple name list)
- [x] TagCreateView (admin only)
  - [x] Template: questions/tag_form.html
- [x] TagUpdateView/DeleteView
- [x] KDListView
  - [x] Template: questions/kd_list.html
  - [x] Filter by grade, subject (Not implemented filter form, just list)
- [x] KDCreateView (admin only)
  - [x] Template: questions/kd_form.html
- [x] KDUpdateView/DeleteView
- [x] Add to questions/urls.py

### Bulk Import Feature
- [x] Create QuestionImportView (admin only)
  - [x] Template: questions/import.html
  - [x] Form: QuestionImportForm (file upload)
  - [x] Preview imported questions before confirm (Skipped for now, direct import)
- [x] Create utils/import_handler.py (impl as services.py)
  - [x] QuestionImporter class (function based)
  - [x] validate() method
  - [x] import_questions() method
  - [x] Error handling & reporting
- [x] Create management command: import_questions
  - [x] questions/management/commands/import_questions.py
  - [x] Handle JSON file path argument
  - [x] Validate & import
  - [x] Print summary
- [x] Test with sample JSON
  ```bash
  python manage.py import_questions data/sample.json
  ```
- [x] Create sample JSON files:
  - [ ] data/matematika-kelas6-pecahan.json (10 soal)
  - [ ] data/matematika-kelas3-penjumlahan.json (10 soal)

---

## Phase 4: Student Management (Day 6-7)

### ARCHITECTURE NOTES (UPDATED) ✅ IMPLEMENTED
- Student is now a User with role='student' (not separate model)
- Parent-Student relationship via ParentStudent model with verification
- Student can self-register independently
- Parent can: create new student, or request link to existing student

### students Views (Parent Perspective) ✅ IMPLEMENTED
- [x] MyStudentsListView (parent: list linked students)
  - [x] Template: students/my_students.html
  - [x] Filter by link status (pending/approved)
  - [x] Card-based layout
- [x] ParentStudentDetailView (parent: view linked student detail)
  - [x] Template: students/student_detail.html
  - [x] Show progress & stats
- [x] StudentCreateByParentView (parent: create new student account)
  - [x] Template: students/create_student.html
  - [x] Form: CreateStudentForm
  - [x] Auto-link with approved status
- [x] StudentLinkView (parent: request link to existing student)
  - [x] Template: students/link_student.html
  - [x] Form: LinkStudentForm
  - [x] Status: pending (requires student verification)
- [x] SelectStudentForQuizView (parent: proxy quiz mode)
  - [x] Template: students/select_for_quiz.html
  - [x] List approved linked students
  - [x] Redirect to quiz with selected student

### students Views (Student Perspective) ✅ IMPLEMENTED
- [x] StudentDashboardView (student's own dashboard)
  - [x] Template: students/dashboard.html
  - [x] Quick stats (questions done, avg accuracy)
  - [x] Recent activity
  - [x] Available quizzes
- [x] LinkRequestListView (student: view pending link requests)
  - [x] Template: students/link_requests.html
  - [x] List pending requests from parents
- [x] LinkRequestActionView (student: approve/reject)
  - [x] POST endpoint for approve/reject action

### Registration Views ✅ IMPLEMENTED
- [x] StudentRegistrationView (Public - student self-register)
  - [x] Template: students/register.html
  - [x] Form: StudentRegistrationForm
- [x] ParentRegistrationView (Public - parent register)
  - [x] Template: students/register_parent.html
  - [x] Form: ParentRegistrationForm

### students/urls.py ✅ IMPLEMENTED
- [x] Create students/urls.py
- [x] Include in main urls.py
- [x] Update URL patterns for new architecture

### Testing ✅ VERIFIED (2026-01-13)
- [x] Test parent creating new student
  - Parent testparent created student siswa1 (Ahmad Putra, grade 4)
  - Auto-linked with approved status
- [x] Test parent requesting link to existing student
  - ParentStudent model tested via shell
- [x] Test student approving/rejecting link request
  - LinkRequestListView and LinkRequestActionView implemented
- [x] Test proxy quiz mode (parent runs quiz for student)
  - Parent (testparent) ran quiz for student (siswa1)
  - QuizSession correctly stored: is_proxy_mode=True, proxy_user=testparent
  - Score 100%, all attempts recorded with correct student FK

---

## Phase 5: Quiz Management (Day 8-10)

### Models (quizzes App)
- [x] Quiz (title, description, grade, subject, time_limit, questions M2M)
- [x] QuizSession (student, quiz, started_at, completed_at, score, passed)
  - [x] **UPDATE**: Add grade field for subject filtering ✅ DONE
  - [x] **UPDATE**: Add is_proxy_mode boolean ✅ DONE
  - [x] **UPDATE**: Add proxy_user FK (parent who runs proxy quiz) ✅ DONE
  - [x] **UPDATE**: student FK now points to User (not Student model) ✅ DONE
- [x] QuestionResponse (Stored in analytics.Attempt)

### Proxy Quiz Mode (NEW) ✅ IMPLEMENTED
- [x] SelectStudentView (parent selects student before quiz)
  - [x] Template: students/select_for_quiz.html
- [x] Start quiz in proxy mode:
  - [x] Set is_proxy_mode = True
  - [x] Set proxy_user = current parent user
  - [x] Set student = selected student
- [x] Views support both direct (student) and proxy (parent) modes
- [x] Grade-based filtering in quiz list

### Parent/Admin Views (Quiz Management)
- [x] QuizListView (List Kuis)
  - [x] Template: quizzes/list.html
- [x] QuizCreateView
  - [x] Template: quizzes/form.html
- [x] QuizDetailView (Manage Questions)
  - [x] Template: quizzes/detail.html
  - [x] List questions in quiz
  - [x] Remove question from quiz
- [x] QuizUpdateView
- [x] QuizDeleteView
- [x] QuizQuestionAddView (Search & Add Questions)
  - [x] Template: quizzes/add_questions.html

### Student/Proxy Views (Taking Quiz) ✅ UPDATED FOR PROXY MODE
- [x] StudentQuizListView (List Kuis Tersedia)
  - [x] Template: quizzes/student_list.html
  - [x] Proxy mode banner
  - [x] Pass student_id and proxy params to quiz URLs
- [x] QuizTakeView (Mengerjakan Kuis)
  - [x] Template: quizzes/take_quiz.html
  - [x] Timer Logic
  - [x] Submit Answer Logic
  - [x] Proxy mode support with hidden fields
- [x] QuizResultView (Hasil Kuis)
  - [x] Template: quizzes/result.html
  - [x] Proxy mode navigation




### Quiz Completion
- [x] QuizReviewView (Implicit in Single-Page Quiz Form)
- [x] QuizCompleteView (Implemented in QuizTakeView.finish_quiz)
- [x] QuizResultView (Duplicate - Done)
- [x] QuizDetailedReviewView (Included in QuizResultView)

### Quiz URLs
- [x] Create quizzes/urls.py
- [x] Include in main urls.py
- [x] Test complete quiz flow

---

## Phase 6: Analytics & Reporting (Day 11-13)

### Metrics Calculation
- [x] Create analytics/metrics.py
  - [x] StudentMetrics class
  - [x] get_accuracy(student)
  - [x] get_strengths(student)
  - [x] get_weaknesses(student)
  - [x] get_subject_performance(student)
  - [x] get_recent_activity(student, days)
  - [x] get_accuracy_trend(student, days)
- [x] get_student_dashboard_context() helper function

### Student Progress Dashboard
- [x] ProgressDashboardView (student)
  - [x] Template: analytics/progress.html
  - [x] Overview stats cards (Total attempts, Accuracy, XP)
  - [x] Subject performance progress bars
  - [x] Quiz statistics
  - [x] Strengths/Weaknesses analysis
- [x] Updated Student Dashboard with real data
  - [x] Template: students/dashboard.html
  - [x] Real-time stats from metrics.py

### Admin Analytics Dashboard
- [x] AnalyticsDashboardView (admin/pengajar)
  - [x] Template: analytics/admin_dashboard.html
  - [x] Student selector dropdown
  - [x] Stats overview cards
  - [x] Subject performance
  - [x] Strengths/Weaknesses analysis
- [x] StudentAttemptHistoryView
  - [x] Template: analytics/attempt_history.html
  - [x] Paginated attempt history

### Analytics URLs
- [x] Create analytics/urls.py
- [x] Include in main urls.py
- [x] Add Analytics link to navbar

### Tag Analytics (Skill Heatmap)
- [x] TagAnalyticsView
  - [x] Template: analytics/tag_heatmap.html
  - [x] Calculate accuracy per tag
  - [x] Identify strengths (>80% accuracy)
  - [x] Identify weaknesses (<60% accuracy)
  - [x] Visual heatmap (color-coded grid)
- [x] get_tag_performance() method in StudentMetrics

### KD Coverage
- [x] KDCoverageView
  - [x] Template: analytics/kd_coverage.html
  - [x] List all KD for grade
  - [x] Show coverage %
  - [x] Show mastery level per KD
  - [x] Progress bars
- [x] get_kd_coverage() method in StudentMetrics

### Reports
- [x] Create analytics/reports.py
  - [x] generate_student_report_csv(student)
  - [x] generate_class_summary_csv(grade)
- [x] ExportStudentReportView - CSV export for individual student
- [x] ExportClassSummaryView - CSV export for class summary
- [ ] PDF export functionality (Optional - requires WeasyPrint/ReportLab)

### Verification
- [x] Test all analytics views
- [x] Verify CSV export

---

## Phase 7: UI/UX Polish (Day 14-15)

### UI Layout Standardization (Referensi: Spike Admin)
**Reference:** https://spike-react-tailwind-main.netlify.app/

#### Base Layout Templates
- [x] Create `templates/layouts/base_dashboard.html` (Admin + Student Dashboard)
  - [x] Fixed sidebar (~250px) with navigation menu
  - [x] Top navbar with user menu
  - [x] Main content area with padding
  - [x] Mobile-responsive sidebar (collapsible)
- [x] Create `templates/layouts/base_auth.html` (Login/Register)
  - [x] Centered card layout for auth pages
  - [x] Clean minimal design

#### Reusable Partial Components
- [x] Create `templates/components/card.html`
- [x] Create `templates/components/page_header.html`
- [x] Create `templates/components/badge.html`
- [x] Create `templates/components/table.html` wrapper
- [x] Create `templates/components/empty_state.html`

#### Sidebar Navigation & Header ✅ COMPLETED
- [x] Create `templates/components/sidebar.html`
- [x] Create `templates/components/header.html`
- [x] Active state styling
- [x] **User role-based menu visibility**
  - [x] Parent menu: Kelola Anak (Siswa Saya, Dampingi Kuis)
  - [x] Admin menu: Materi & Soal (Bank Soal, Tags, KD), Aktivitas (Kuis, Analytics)
  - [x] Student menu: Belajar (Kuis Tersedia, Progress), Akun (Permintaan Orang Tua)
- [x] Implement mobile sidebar (hamburger menu)

#### Role-Based Dashboards ✅ COMPLETED
- [x] **Parent Dashboard** (`students/parent_dashboard.html`)
  - [x] Gradient hero section with welcome message
  - [x] Stats cards (Siswa Terhubung, Kuis Dikerjakan, Permintaan Tertunda)
  - [x] Students list with quick actions
  - [x] Recent quiz activity section
  - [x] Empty state for no students
- [x] **Student Dashboard** (`students/dashboard.html`)
  - [x] Gradient hero with avatar and XP badge
  - [x] Stats grid (XP, Soal Dikerjakan, Akurasi, Kuis Lulus)
  - [x] Subject performance with color-coded progress bars
  - [x] Weekly activity chart
  - [x] Quick action cards
- [x] **Dashboard Router** (`core/views.py`)
  - [x] Redirect student -> StudentDashboardView
  - [x] Redirect parent -> ParentDashboardView
  - [x] Redirect admin -> Analytics Dashboard

#### Template Migration ✅ COMPLETED
- [x] Migrate Auth templates (Login, Register, Password Reset)
- [x] Migrate all "List" views to use standard Table component
- [x] Migrate all "Detail" views to use standard Card component

#### Admin Verification (Immediate Next Step)
- [ ] **Ensure Django Admin features are fully functional**
  - [ ] Accounts: Test User CRUD & Parent approval
  - [ ] Subjects: Test Subject/Topic CRUD & inlines
  - [ ] Questions: Test Question CRUD, preview, and filters
  - [ ] Quizzes: Test Quiz creation & detailed session view
  - [ ] Analytics: Verify read-only views for Attempts
- [ ] **Test CRUD operations for all admin views**


#### Page Migration to New Layout
- [x] Migrate Students pages
  - [x] students/list.html
  - [x] students/detail.html
  - [x] students/form.html
  - [x] students/dashboard.html ✅ REDESIGNED
  - [x] students/parent_dashboard.html ✅ NEW
  - [x] students/my_students.html
  - [x] students/select_for_quiz.html
  - [x] students/link_requests.html
- [x] **Migrate Questions Templates**
    - [x] List (`questions/list.html`) - Table layout, filter.
    - [x] Detail (`questions/detail.html`) - Clean layout.
    - [x] Form (`questions/form.html`) - Standard form.
    - [x] Import (`questions/import.html`) - File upload.
- [x] **Migrate Quizzes Templates**
    - [x] List (`quizzes/list.html`) - Table.
    - [x] Detail (`quizzes/detail.html`) - Layout.
    - [x] Form (`quizzes/form.html`) - Standard form.
    - [x] Student List (`quizzes/student_list.html`) - Grid + Proxy mode.
    - [x] Take Quiz (`quizzes/take_quiz.html`) - Clean UI + Proxy banner.
    - [x] Result (`quizzes/result.html`) - Review UI + Proxy mode.
- [x] **Migrate Analytics Templates**
    - [x] Admin Dashboard (`analytics/admin_dashboard.html`) - Metrics Grid.
    - [x] Heatmap (`analytics/tag_heatmap.html`) - Visuals.
    - [x] KD Coverage (`analytics/kd_coverage.html`) - Progress bars.
    - [x] Progress (`analytics/progress.html`) - Student view.
    - [x] Attempt History (`analytics/attempt_history.html`) - History table.
- [x] Migrate Auth pages
  - [x] accounts/login.html
  - [x] accounts/profile.html

### Responsive Design
- [ ] Test all pages on mobile viewport (375px)
- [ ] Test on tablet viewport (768px)
- [ ] Test on desktop viewport (1280px+)
- [ ] Sidebar collapse to hamburger menu on mobile
- [ ] Table horizontal scroll on mobile
- [ ] Card stack layout on mobile
- [ ] Quiz interface touch-friendly on tablet

### HTMX Enhancements
- [ ] Add loading indicators (htmx-indicator)
  - [ ] Spinner component
  - [ ] Skeleton loading (optional)
- [ ] Add smooth transitions (CSS)
  - [ ] Page transition effects
  - [ ] Modal animations
- [ ] Error handling (htmx:responseError event)
  - [ ] Toast notification for errors
  - [ ] Retry mechanism
- [ ] Implement optimistic UI updates
- [ ] Test all HTMX interactions

### Accessibility
- [ ] Add ARIA labels to all interactive elements
- [ ] Keyboard navigation (quiz interface)
- [ ] Focus indicators (visible focus ring)
- [ ] Color contrast check (WCAG AA)
- [ ] Screen reader testing (basic)

### Forms & Validation
- [ ] Standardize form input styling
  - [ ] Input focus states (blue ring)
  - [ ] Error state styling (red border)
  - [ ] Disabled state styling
- [ ] Client-side validation (HTML5)
- [ ] Django form validation messages
- [ ] Error display styling (below input)
- [ ] Success messages (Django messages framework)
- [ ] Toast notifications (Alpine.js component)

### Print Styles
- [ ] Create print.css
- [ ] Quiz results print-friendly
- [ ] Reports print-friendly
- [ ] Hide navigation on print
- [ ] Test print preview

### Math Rendering
- [ ] Integrate KaTeX in question display
- [ ] Test LaTeX syntax rendering
- [ ] Fallback for parse errors
- [ ] Support common math symbols

### Image Optimization
- [ ] Implement image compression on upload
- [ ] Generate thumbnails (Pillow)
- [ ] Lazy loading (loading="lazy")
- [ ] Test with various image sizes

---

## Phase 8: Testing (Day 16-17)

### Unit Tests
- [ ] Test models (accounts, students, questions, quizzes, analytics)
- [ ] Test forms
- [ ] Test validators
- [ ] Test utility functions (import_handler, metrics, etc)
- [ ] Run tests:
  ```bash
  pytest
  ```
- [ ] Achieve >70% coverage

### Integration Tests
- [ ] Test quiz flow (end-to-end)
- [ ] Test import questions flow
- [ ] Test analytics calculation
- [ ] Test report generation

### Manual Testing
- [ ] Create test data (students, questions, quiz sessions, attempts)
- [ ] Test as admin role
- [ ] Test as pengajar role
- [ ] Test as student role
- [ ] Test all CRUD operations
- [ ] Test all filters
- [ ] Test quiz with timer
- [ ] Test quiz without timer
- [ ] Test analytics accuracy
- [ ] Test report exports

### Edge Cases
- [ ] Test with 0 questions
- [ ] Test with 100+ questions
- [ ] Test quiz timeout (auto-submit)
- [ ] Test duplicate question in quiz
- [ ] Test invalid JSON import
- [ ] Test permission denials

### Performance Testing
- [ ] Test with 1000+ questions
- [ ] Test with 100+ attempts
- [ ] Query optimization (use django-debug-toolbar)
- [ ] Identify N+1 queries
- [ ] Add select_related / prefetch_related
- [ ] Test page load times (<2s target)

---

## Phase 9: VPS Deployment (Day 18-19)

### VPS Preparation
- [ ] Provision VPS (Domainesia/DigitalOcean)
  - [ ] 2 CPU cores minimum
  - [ ] 2GB RAM minimum
  - [ ] 20GB SSD minimum
  - [ ] Ubuntu 22.04 LTS
- [ ] SSH access setup
  ```bash
  ssh root@your-vps-ip
  ```
- [ ] Create non-root user
  ```bash
  adduser banksoal
  usermod -aG sudo banksoal
  su - banksoal
  ```
- [ ] Update system
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

### Install Dependencies
- [ ] Install Python 3.11
  ```bash
  sudo apt install python3.11 python3.11-venv python3-pip
  ```
- [ ] Install PostgreSQL
  ```bash
  sudo apt install postgresql postgresql-contrib
  ```
- [ ] Install Nginx
  ```bash
  sudo apt install nginx
  ```
- [ ] Install Supervisor (or use systemd)
  ```bash
  sudo apt install supervisor
  ```
- [ ] Install Certbot (SSL)
  ```bash
  sudo apt install certbot python3-certbot-nginx
  ```
- [ ] Install Git
  ```bash
  sudo apt install git
  ```
- [ ] Install Node.js (for Tailwind build)
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt install nodejs
  ```

### PostgreSQL Setup (Production)
- [ ] Create database & user
  ```bash
  sudo -u postgres psql
  CREATE DATABASE banksoal_db;
  CREATE USER banksoal WITH PASSWORD 'secure_production_password';
  GRANT ALL PRIVILEGES ON DATABASE banksoal_db TO banksoal;
  \q
  ```
- [ ] Test connection
- [ ] Configure PostgreSQL for remote access (if needed)

### Deploy Application
- [ ] Clone repository
  ```bash
  cd /home/banksoal
  git clone <your-repo-url> app
  cd app
  ```
- [ ] Create virtual environment
  ```bash
  python3.11 -m venv venv
  source venv/bin/activate
  ```
- [ ] Install dependencies
  ```bash
  pip install -r requirements/production.txt
  ```
- [ ] Create .env file (production)
  ```bash
  cp .env.example .env
  nano .env  # Edit with production values
  ```
- [ ] Build Tailwind CSS
  ```bash
  npm install
  npm run build
  ```
- [ ] Collect static files
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] Run migrations
  ```bash
  python manage.py migrate
  ```
- [ ] Create superuser
  ```bash
  python manage.py createsuperuser
  ```
- [ ] Test with runserver (temporary)
  ```bash
  python manage.py runserver 0.0.0.0:8000
  # Visit http://vps-ip:8000
  ```

### Gunicorn Setup
- [ ] Create gunicorn_config.py (copy from spec)
- [ ] Test Gunicorn
  ```bash
  gunicorn --config gunicorn_config.py config.wsgi:application
  ```
- [ ] Create systemd service file
  ```bash
  sudo nano /etc/systemd/system/banksoal.service
  # Copy config from spec
  ```
- [ ] Enable & start service
  ```bash
  sudo systemctl enable banksoal
  sudo systemctl start banksoal
  sudo systemctl status banksoal
  ```

### Nginx Setup
- [ ] Create Nginx config
  ```bash
  sudo nano /etc/nginx/sites-available/banksoal
  # Copy config from spec (without SSL first)
  ```
- [ ] Enable site
  ```bash
  sudo ln -s /etc/nginx/sites-available/banksoal /etc/nginx/sites-enabled/
  ```
- [ ] Test config
  ```bash
  sudo nginx -t
  ```
- [ ] Restart Nginx
  ```bash
  sudo systemctl restart nginx
  ```
- [ ] Test via domain (HTTP)
  ```
  http://banksoal.yourdomain.com
  ```

### SSL Setup
- [ ] Point domain to VPS IP (DNS A record)
- [ ] Wait for DNS propagation (check with `dig`)
- [ ] Obtain SSL certificate
  ```bash
  sudo certbot --nginx -d banksoal.yourdomain.com
  ```
- [ ] Test HTTPS
  ```
  https://banksoal.yourdomain.com
  ```
- [ ] Setup auto-renewal
  ```bash
  sudo certbot renew --dry-run
  ```

### Firewall Setup
- [ ] Configure UFW
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  sudo ufw status
  ```

### Logging
- [ ] Create log directories
  ```bash
  mkdir -p /home/banksoal/logs
  ```
- [ ] Configure Django logging (settings)
- [ ] Test log rotation (logrotate)

---

## Phase 10: Post-Deployment (Day 19-20)

### Backup Setup
- [ ] Create backup script (backup_db.sh)
  ```bash
  #!/bin/bash
  pg_dump -U banksoal banksoal_db | gzip > /home/banksoal/backups/db-$(date +%Y%m%d).sql.gz
  find /home/banksoal/backups -name "db-*.sql.gz" -mtime +30 -delete
  ```
- [ ] Make executable
  ```bash
  chmod +x /home/banksoal/scripts/backup_db.sh
  ```
- [ ] Setup cron job (daily backup)
  ```bash
  crontab -e
  # Add: 0 2 * * * /home/banksoal/scripts/backup_db.sh
  ```
- [ ] Test backup script
- [ ] Setup media backup (weekly)

### Monitoring
- [ ] Setup basic uptime monitoring (UptimeRobot / Pingdom)
- [ ] Monitor disk space
  ```bash
  df -h
  ```
- [ ] Monitor memory
  ```bash
  free -h
  ```
- [ ] Check logs regularly
  ```bash
  tail -f /home/banksoal/logs/django.log
  tail -f /var/log/nginx/banksoal_error.log
  ```

### Performance Optimization
- [ ] Enable Gzip compression (Nginx)
- [ ] Browser caching headers (Nginx)
- [ ] Database query optimization
- [ ] Consider Redis for caching (optional)

### Security Hardening
- [ ] Disable root SSH login
- [ ] Change default SSH port (optional)
- [ ] Install fail2ban
  ```bash
  sudo apt install fail2ban
  ```
- [ ] Regular security updates
  ```bash
  sudo apt update && sudo apt upgrade
  ```

### Documentation
- [ ] Create deployment guide (DEPLOYMENT.md)
- [ ] Create user manual (for ortu/pengajar)
- [ ] Document backup/restore procedure
- [ ] Document common issues & solutions

---

## Phase 11: Content Creation (Ongoing)

### Initial Question Set
- [ ] Generate 30 soal Matematika kelas 6
  - [ ] 10 Bilangan Bulat (mudah)
  - [ ] 10 Pecahan (mudah, sedang)
  - [ ] 10 Geometri (sedang, sulit)
- [ ] Generate 30 soal Matematika kelas 3
  - [ ] 10 Penjumlahan/Pengurangan
  - [ ] 10 Perkalian/Pembagian
  - [ ] 10 Bangun Datar
- [ ] Generate 20 soal IPA kelas 6
  - [ ] 10 Sistem Tata Surya
  - [ ] 10 Energi & Perubahannya
- [ ] Generate 20 soal IPA kelas 3
  - [ ] 10 Makhluk Hidup
  - [ ] 10 Gerak Benda

### Import Content
- [ ] Create JSON files (organized by subject/topic/grade)
- [ ] Import via management command
  ```bash
  python manage.py import_questions data/matematika-6-bilangan-bulat.json
  python manage.py import_questions data/matematika-6-pecahan.json
  # ... etc
  ```
- [ ] Verify in admin panel
- [ ] Test questions in frontend

### Tag & KD Mapping
- [ ] Create comprehensive tag list
  - [ ] Skill tags
  - [ ] Topic tags
  - [ ] Difficulty tags
- [ ] Create KD list for kelas 3 & 6 (all subjects)
- [ ] Map existing questions to tags & KD
- [ ] Bulk update via admin

### Content Iteration
- [ ] Review questions dengan istri
- [ ] Fix errors or ambiguities
- [ ] Add more questions based on usage
- [ ] Target: 500+ questions total

---

## Quick Commands Reference

### Development
```bash
# Activate venv
source venv/bin/activate

# Run dev server
python manage.py runserver

# Run Tailwind watch
npm run dev

# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collectstatic
python manage.py collectstatic

# Import questions
python manage.py import_questions data/sample.json

# Run tests
pytest

# Shell
python manage.py shell
```

### Production
```bash
# SSH to VPS
ssh banksoal@your-vps-ip

# Activate venv
cd /home/banksoal/app
source venv/bin/activate

# Pull latest code
git pull origin main

# Install new dependencies (if any)
pip install -r requirements/production.txt

# Run migrations
python manage.py migrate

# Collectstatic
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart banksoal
sudo systemctl restart nginx

# View logs
tail -f /home/banksoal/logs/django.log
tail -f /var/log/nginx/banksoal_error.log

# Check service status
sudo systemctl status banksoal
sudo systemctl status nginx
sudo systemctl status postgresql
```

---

## Estimated Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 0 | 1 day | Dev environment ready |
| Phase 1 | 2 days | Database models & admin |
| Phase 2 | 2 days | Auth & base templates |
| Phase 3 | 2 days | Question management + import |
| Phase 4 | 1 day | Student management |
| Phase 5 | 3 days | Quiz engine (complex) |
| Phase 6 | 3 days | Analytics & reports |
| Phase 7 | 2 days | UI/UX polish |
| Phase 8 | 2 days | Testing |
| Phase 9 | 2 days | VPS deployment |
| Phase 10 | 1 day | Post-deployment setup |
| **Total** | **21 days** | **Production-ready app** |

Phase 11 (Content) is ongoing and can start after Phase 3.

---

## Priority Checklist (MVP)

**Must Have (MVP):**
- [x] User authentication (admin, pengajar, student roles)
- [x] Student management
- [x] Question bank with tagging
- [x] Bulk import JSON
- [x] Practice mode quiz
- [x] Timed quiz mode
- [x] Basic progress tracking
- [x] Basic analytics dashboard

**Should Have (Phase 2):**
- [ ] Custom quiz creation
- [ ] Advanced analytics (tag heatmap, KD coverage)
- [ ] PDF report export
- [ ] Detailed question-level analytics

**Nice to Have (Future):**
- [ ] Real-time collaboration (multiple students same quiz)
- [ ] AI-generated questions
- [ ] Video explanations
- [ ] Mobile app

---

## Notes for Claude Code Execution

### When Creating Models:
- Follow Django best practices (Meta class, __str__, etc)
- Add indexes for frequently queried fields
- Use validators where appropriate
- Consider migrations carefully

### When Writing Views:
- Use class-based views (ListView, DetailView, etc) untuk consistency
- Implement permission checks (mixins/decorators)
- Handle errors gracefully
- Add success messages

### When Writing Templates:
- Use Tailwind utility classes
- Follow component-based structure
- Make responsive (mobile-first)
- Use HTMX for dynamic parts
- Keep templates DRY (use includes, extends)

### When Importing Questions:
- Validate JSON structure thoroughly
- Handle errors without breaking entire import
- Log all operations
- Provide detailed feedback to user

### When Testing:
- Test with realistic data
- Test all user roles
- Test edge cases
- Test performance with large datasets

---

**Ready to Start! Lanjut ke eksekusi dengan Claude Code! 🚀**
