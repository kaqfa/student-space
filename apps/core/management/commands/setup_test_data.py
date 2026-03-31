import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import ParentStudent
from apps.subjects.models import Subject, Topic
from apps.questions.models import Question, Tag, KompetensiDasar
from apps.quizzes.models import Quiz, QuizSession
from apps.analytics.models import Attempt

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with comprehensive test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        # Urutan delete penting karena constraints
        Attempt.objects.all().delete()
        QuizSession.objects.all().delete()
        Quiz.objects.all().delete()
        Question.objects.all().delete()
        Topic.objects.all().delete()
        Subject.objects.all().delete()
        Tag.objects.all().delete()
        KompetensiDasar.objects.all().delete()
        ParentStudent.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete() # Keep superuser if exists

        self.stdout.write('Creating Users...')
        self.create_users()

        self.stdout.write('Creating Academic Content...')
        self.create_academic_content()

        self.stdout.write('Creating Quizzes & Analytics...')
        self.create_quizzes_and_history()

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))

    def create_users(self):
        # 1. Admin (jika belum ada)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
        # 2. Parent
        self.parent = User.objects.create_user(
            username='orangtua',
            email='parent@example.com',
            password='parent123',
            role=User.Role.PARENT,
            first_name='Budi',
            last_name='Santoso'
        )

        # 3. Teacher
        self.teacher = User.objects.create_user(
            username='guru',
            email='guru@example.com',
            password='guru123',
            role=User.Role.PARENT, # Teacher acts as Parent/Admin role context
            first_name='Bu',
            last_name='Sri',
            is_staff=True # Flag as staff for admin access if needed
        )

        # 4. Students (Kelas 3, 4, 5, 6)
        self.students = []
        grades = [3, 4, 5, 6]
        names = ['Andi', 'Budi', 'Citra', 'Dewi']
        
        for i, grade in enumerate(grades):
            student = User.objects.create_user(
                username=f'siswa{grade}',
                email=f'siswa{grade}@example.com',
                password='siswa123',
                role=User.Role.STUDENT,
                first_name=names[i],
                last_name='Pelajar',
                grade=grade
            )
            self.students.append(student)
            
            # Link to parent
            ParentStudent.objects.create(
                parent=self.parent,
                student=student,
                status=ParentStudent.Status.APPROVED
            )

    def create_academic_content(self):
        # Subjects per grade
        subjects_data = {
            'Matematika': ['Pecahan', 'Geometri', 'Statistik Dasar', 'Aljabar Dasar'],
            'IPA': ['Makhluk Hidup', 'Energi', 'Tata Surya', 'Fisika Dasar'],
            'Bahasa Indonesia': ['Tata Bahasa', 'Pemahaman Bacaan', 'Puisi', 'Menulis'],
        }

        self.questions_pool = []
        
        # Create Tags & KD
        tags = [Tag.objects.create(name=t) for t in ['HOTS', 'Mudah', 'Sulit', 'UN', 'Olimpiade']]
        
        for grade in [3, 4, 5, 6]:
            for subj_name, topics in subjects_data.items():
                subject = Subject.objects.create(
                    name=subj_name,
                    grade=grade,
                    icon='book-open',
                    color=random.choice(['#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'])
                )

                # KD per subject per grade
                kd_list = []
                for i in range(1, 4):
                    kd = KompetensiDasar.objects.create(
                        subject=subject,
                        code=f'3.{i}',
                        grade=grade,
                        description=f'Kompetensi Dasar 3.{i} untuk {subj_name} Kelas {grade}'
                    )
                    kd_list.append(kd)
                
                for topic_name in topics:
                    topic = Topic.objects.create(
                        subject=subject,
                        name=topic_name,
                        description=f'Topik {topic_name} dalam {subj_name}'
                    )
                    
                    # Create Questions (5 per topic)
                    for q in range(1, 4):
                        question = Question.objects.create(
                            topic=topic,
                            question_text=f'Soal {subj_name} - {topic_name} untuk kelas {grade} nomor {q}. Berapakah hasilnya?',
                            question_type=Question.Type.PILGAN,
                            difficulty=random.choice([Question.Difficulty.MUDAH, Question.Difficulty.SEDANG, Question.Difficulty.SULIT]),
                            answer_key='A',
                            options=['Jawaban Benar A', 'Jawaban Salah B', 'Jawaban Salah C', 'Jawaban Salah D'],
                            explanation='Penjelasan detail kenapa A benar.',
                            points=10,
                            created_by=self.teacher
                        )
                        # Add random tags and KD
                        question.tags.add(random.choice(tags))
                        if kd_list:
                            question.kompetensi_dasar.add(random.choice(kd_list))
                        question.save()
                        self.questions_pool.append(question)

    def create_quizzes_and_history(self):
        # Create 1 Quiz per Subject for Grade 4 & 5
        active_students = [s for s in self.students if s.grade in [4, 5]]
        
        for student in active_students:
            subjects = Subject.objects.filter(grade=student.grade)
            
            for subject in subjects:
                # Create Quiz
                quiz = Quiz.objects.create(
                    title=f'Latihan Harian {subject.name} Kelas {student.grade}',
                    description='Latihan soal untuk persiapan ujian mingguan',
                    grade=student.grade,
                    subject=subject,
                    time_limit_minutes=30,
                    passing_score=70,
                    created_by=self.teacher,
                    is_active=True
                )
                
                # Add 5 random questions
                questions = Question.objects.filter(topic__subject=subject).order_by('?')[:5]
                quiz.questions.add(*questions)
                
                # Create History (Some passed, some failed)
                passed = random.choice([True, False])
                score = random.randint(75, 100) if passed else random.randint(40, 65)
                
                session = QuizSession.objects.create(
                    student=student,
                    quiz=quiz,
                    score=score,
                    passed=passed,
                    started_at=timezone.now() - timedelta(days=random.randint(1, 7)),
                    completed_at=timezone.now() - timedelta(days=random.randint(1, 7)) + timedelta(minutes=25)
                )
                
                # Create Attempts for this session
                for q in questions:
                    is_correct = True if passed else random.choice([True, False])
                    Attempt.objects.create(
                        quiz_session=session,
                        student=student,
                        question=q,
                        answer_given=q.answer_key if is_correct else 'B',
                        is_correct=is_correct,
                        points_earned=q.points if is_correct else 0,
                        time_taken=random.randint(30, 120)
                    )

        # Create Active Proxy Quiz Session (In Progress)
        proxy_student = self.students[-1] # Kelas 6
        parent = self.parent
        
        # Get grade 6 subject
        subj_ipa = Subject.objects.filter(grade=6, name='IPA').first()
        if subj_ipa:
            # Create Quiz
            quiz_ipa = Quiz.objects.create(
                title='Ujian Simulasi IPA Kelas 6',
                grade=6,
                subject=subj_ipa,
                time_limit_minutes=60,
                passing_score=75,
                created_by=self.teacher,
                is_active=True
            )
            q_ipa = Question.objects.filter(topic__subject=subj_ipa)[:3]
            quiz_ipa.questions.add(*q_ipa)
            
            # Start Proxy Session (Parent doing for Student) - IN PROGRESS
            QuizSession.objects.create(
                student=proxy_student,
                quiz=quiz_ipa,
                is_proxy_mode=True,
                proxy_user=parent,
                started_at=timezone.now() - timedelta(minutes=5)
            )
