from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.http import Http404, HttpResponseRedirect

from apps.analytics.models import Attempt
from apps.accounts.mixins import ParentOrAdminMixin, StudentRequiredMixin, ParentRequiredMixin
from apps.accounts.models import ParentStudent
from .models import Quiz, QuizSession
from .forms import QuizForm
from apps.questions.models import Question

User = get_user_model()


# ============================================================
# ADMIN/PARENT VIEWS (Quiz Management)
# ============================================================

class QuizListView(ParentOrAdminMixin, ListView):
    """List all quizzes for admin/parent."""
    model = Quiz
    template_name = "quizzes/list.html"
    context_object_name = "quizzes"
    paginate_by = 20

    def get_queryset(self):
        queryset = Quiz.objects.select_related('subject', 'created_by')
        return queryset.order_by('-created_at')


class QuizCreateView(ParentOrAdminMixin, CreateView):
    """Create a new quiz."""
    model = Quiz
    form_class = QuizForm
    template_name = "quizzes/form.html"
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Kuis berhasil dibuat. Silakan tambahkan soal.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quizzes:detail', kwargs={'pk': self.object.pk})


class QuizUpdateView(ParentOrAdminMixin, UpdateView):
    """Update quiz details."""
    model = Quiz
    form_class = QuizForm
    template_name = "quizzes/form.html"
    
    def get_success_url(self):
        return reverse_lazy('quizzes:detail', kwargs={'pk': self.object.pk})
        
    def form_valid(self, form):
        messages.success(self.request, "Detail kuis diperbarui.")
        return super().form_valid(form)


class QuizDetailView(ParentOrAdminMixin, DetailView):
    """View quiz details and questions."""
    model = Quiz
    template_name = "quizzes/detail.html"
    context_object_name = "quiz"


class QuizDeleteView(ParentOrAdminMixin, DeleteView):
    """Delete a quiz."""
    model = Quiz
    template_name = "quizzes/confirm_delete.html"
    success_url = reverse_lazy('quizzes:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Kuis berhasil dihapus.")
        return super().delete(request, *args, **kwargs)


class QuizQuestionAddView(ParentOrAdminMixin, ListView):
    """Add questions to a quiz."""
    model = Question
    template_name = "quizzes/add_questions.html"
    context_object_name = "questions"
    paginate_by = 50
    
    def get_queryset(self):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
        queryset = Question.objects.filter(
            topic__subject=self.quiz.subject
        ).exclude(quizzes=self.quiz)
        
        topic_id = self.request.GET.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(question_text__icontains=search)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        return context
    
    def post(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
        question_ids = request.POST.getlist('question_ids')
        if question_ids:
            questions = Question.objects.filter(id__in=question_ids)
            self.quiz.questions.add(*questions)
            messages.success(request, f"{len(questions)} soal ditambahkan ke kuis.")
        else:
            messages.warning(request, "Tidak ada soal yang dipilih.")
            
        return redirect('quizzes:detail', pk=self.quiz.pk)


class QuizQuestionRemoveView(ParentOrAdminMixin, View):
    """Remove a question from a quiz."""
    def post(self, request, pk, question_id):
        quiz = get_object_or_404(Quiz, pk=pk)
        question = get_object_or_404(Question, pk=question_id)
        quiz.questions.remove(question)
        messages.success(request, "Soal dihapus dari kuis.")
        return redirect('quizzes:detail', pk=pk)


# ============================================================
# STUDENT VIEWS (Taking Quizzes)
# ============================================================

class StudentQuizListView(LoginRequiredMixin, ListView):
    """
    List available quizzes for students.
    Supports both direct access (student) and proxy mode (parent).
    """
    model = Quiz
    template_name = "quizzes/student_list.html"
    context_object_name = "quizzes"
    
    def get_student(self):
        """Get the student user (either current user or proxy target)."""
        user = self.request.user
        
        # Check for proxy mode
        student_id = self.request.GET.get('student_id')
        proxy = self.request.GET.get('proxy')
        
        if proxy and student_id and user.role == User.Role.PARENT:
            # Verify parent has access to this student
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
            is_linked = ParentStudent.objects.filter(
                parent=user,
                student=student,
                status=ParentStudent.Status.APPROVED
            ).exists()
            if not is_linked:
                raise Http404("Siswa tidak terhubung dengan Anda.")
            return student, True  # (student, is_proxy)
        
        # Direct student access
        if user.role == User.Role.STUDENT:
            return user, False
        
        raise Http404("Akses tidak valid.")
    
    def get_queryset(self):
        student, _ = self.get_student()
        
        if not student or not student.grade:
            return Quiz.objects.none()
        
        return Quiz.objects.filter(
            grade=student.grade, 
            is_active=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student, is_proxy = self.get_student()
        context['student'] = student
        context['is_proxy'] = is_proxy
        context['student_id'] = student.pk
        context['proxy_param'] = '&proxy=1' if is_proxy else ''
        return context


class QuizTakeView(LoginRequiredMixin, DetailView):
    """
    View for taking a quiz.
    Supports both direct (student) and proxy (parent) modes.
    """
    model = Quiz
    template_name = "quizzes/take_quiz.html"
    context_object_name = "quiz"

    def get_student(self):
        """Get the student and determine proxy mode."""
        user = self.request.user
        
        # Check for proxy mode
        student_id = self.request.GET.get('student_id') or self.request.POST.get('student_id')
        proxy = self.request.GET.get('proxy') or self.request.POST.get('proxy')
        
        if proxy and student_id and user.role == User.Role.PARENT:
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
            is_linked = ParentStudent.objects.filter(
                parent=user,
                student=student,
                status=ParentStudent.Status.APPROVED
            ).exists()
            if not is_linked:
                raise Http404("Siswa tidak terhubung dengan Anda.")
            return student, True, user  # (student, is_proxy, proxy_user)
        
        # Direct student access
        if user.role == User.Role.STUDENT:
            return user, False, None
        
        raise Http404("Akses tidak valid.")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        student, is_proxy, proxy_user = self.get_student()
        
        # Check for existing active session
        session, created = QuizSession.objects.get_or_create(
            student=student, 
            quiz=self.object,
            completed_at__isnull=True,
            defaults={
                'score': 0,
                'grade': student.grade or self.object.grade,
                'is_proxy_mode': is_proxy,
                'proxy_user': proxy_user if is_proxy else None,
            }
        )
        
        # Update proxy info if existing session
        if not created and is_proxy and not session.is_proxy_mode:
            session.is_proxy_mode = True
            session.proxy_user = proxy_user
            session.save(update_fields=['is_proxy_mode', 'proxy_user'])
        
        # Calculate time remaining
        remaining_seconds = None
        if self.object.time_limit_minutes:
            elapsed = (timezone.now() - session.started_at).total_seconds()
            remaining_seconds = (self.object.time_limit_minutes * 60) - elapsed
            if remaining_seconds <= 0:
                messages.warning(request, "Waktu habis!")
                return self.finish_quiz(session)

        context = self.get_context_data(object=self.object)
        context['session'] = session
        context['remaining_seconds'] = remaining_seconds
        context['student'] = student
        context['is_proxy'] = is_proxy
        context['student_id'] = student.pk
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        student, is_proxy, proxy_user = self.get_student()
        session = get_object_or_404(
            QuizSession, 
            student=student, 
            quiz=self.object, 
            completed_at__isnull=True
        )
        
        return self.finish_quiz(session, request.POST)

    def finish_quiz(self, session, post_data=None):
        quiz = session.quiz
        earned_points = 0
        
        if post_data:
            for question in quiz.questions.all():
                answer_key = "question_" + str(question.id)
                answer_given = post_data.get(answer_key, "").strip().upper()
                
                is_correct = False
                if question.question_type == 'pilgan':
                    if answer_given == question.answer_key:
                        is_correct = True
                
                Attempt.objects.create(
                    student=session.student,
                    question=question,
                    quiz_session=session,
                    answer_given=answer_given,
                    is_correct=is_correct,
                    time_taken=0 
                )
                
                if is_correct:
                    earned_points += question.points
        
        max_points = quiz.total_points
        if max_points > 0:
            final_score = (earned_points / max_points) * 100
        else:
            final_score = 0
            
        session.score = final_score
        session.passed = final_score >= quiz.passing_score
        session.completed_at = timezone.now()
        session.save()
        
        student_name = session.student.get_full_name() or session.student.username
        
        if session.is_proxy_mode:
            messages.success(
                self.request, 
                f"Kuis selesai! Skor {student_name}: {round(final_score, 1)}%"
            )
            result_url = reverse('quizzes:result', kwargs={'pk': quiz.pk})
            return HttpResponseRedirect(f'{result_url}?student_id={session.student.pk}&proxy=1')
        else:
            messages.success(self.request, f"Kuis selesai! Skor kamu: {round(final_score, 1)}%")
            return redirect('quizzes:result', pk=quiz.pk)


class QuizResultView(LoginRequiredMixin, DetailView):
    """
    View quiz results.
    Supports both direct (student) and proxy (parent) modes.
    """
    model = Quiz
    template_name = "quizzes/result.html"
    context_object_name = "quiz"
    
    def get_student(self):
        """Get the student and determine proxy mode."""
        user = self.request.user
        
        student_id = self.request.GET.get('student_id')
        proxy = self.request.GET.get('proxy')
        
        if proxy and student_id and user.role == User.Role.PARENT:
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
            is_linked = ParentStudent.objects.filter(
                parent=user,
                student=student,
                status=ParentStudent.Status.APPROVED
            ).exists()
            if not is_linked:
                raise Http404("Siswa tidak terhubung dengan Anda.")
            return student, True
        
        if user.role == User.Role.STUDENT:
            return user, False
        
        raise Http404("Akses tidak valid.")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student, is_proxy = self.get_student()
        
        # Get the most recent completed session (allows retakes)
        session = QuizSession.objects.filter(
            quiz=self.object, 
            student=student, 
            completed_at__isnull=False
        ).order_by('-completed_at').first()
        
        if not session:
            raise Http404("Belum ada hasil kuis yang tersedia.")
        context['session'] = session
        context['attempts'] = session.attempts.select_related('question').all()
        context['student'] = student
        context['is_proxy'] = is_proxy
        return context


# ============================================================
# PARENT PROXY MODE HELPER
# ============================================================

class ProxyQuizSelectStudentView(ParentRequiredMixin, ListView):
    """
    Parent selects a student before starting a proxy quiz.
    This view shows available quizzes after student selection.
    """
    model = Quiz
    template_name = "quizzes/proxy_select_student.html"
    context_object_name = "quizzes"
    
    def get_queryset(self):
        student_id = self.request.GET.get('student_id')
        if not student_id:
            return Quiz.objects.none()
        
        student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        
        # Verify parent access
        is_linked = ParentStudent.objects.filter(
            parent=self.request.user,
            student=student,
            status=ParentStudent.Status.APPROVED
        ).exists()
        
        if not is_linked:
            return Quiz.objects.none()
        
        self.selected_student = student
        
        return Quiz.objects.filter(
            grade=student.grade,
            is_active=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = getattr(self, 'selected_student', None)
        
        # Get all linked students for selection
        context['students'] = User.objects.filter(
            parent_links__parent=self.request.user,
            parent_links__status=ParentStudent.Status.APPROVED,
            role=User.Role.STUDENT
        ).order_by('grade', 'first_name')
        
        return context
