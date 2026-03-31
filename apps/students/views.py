from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404

from .forms import (
    StudentRegistrationForm, 
    ParentRegistrationForm,
    CreateStudentForm,
    LinkStudentForm,
    StudentProfileUpdateForm,
)
from apps.accounts.models import ParentStudent
from apps.accounts.mixins import (
    StudentRequiredMixin, 
    ParentRequiredMixin, 
    ParentOrAdminMixin,
)

User = get_user_model()


# ============================================================
# PUBLIC REGISTRATION VIEWS
# ============================================================

class StudentRegistrationView(CreateView):
    """Student self-registration view."""
    form_class = StudentRegistrationForm
    template_name = "students/register.html"
    success_url = reverse_lazy("students:dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Selamat datang, {user.first_name}! Akun berhasil dibuat.")
        return HttpResponseRedirect(self.success_url)


class ParentRegistrationView(CreateView):
    """Parent registration view."""
    form_class = ParentRegistrationForm
    template_name = "students/register_parent.html"
    success_url = reverse_lazy("students:my_students")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Selamat datang, {user.first_name}! Akun orang tua berhasil dibuat.")
        return HttpResponseRedirect(self.success_url)


# ============================================================
# STUDENT VIEWS (For users with role='student')
# ============================================================

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    """Dashboard view for students."""
    template_name = "students/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        context['student'] = student
        
        # Get dashboard metrics
        from apps.analytics.metrics import StudentMetrics
        metrics = StudentMetrics(student)
        
        context['total_attempts'] = metrics.get_total_attempts()
        context['accuracy'] = metrics.get_accuracy()
        context['total_xp'] = metrics.get_total_xp()
        context['recent_activity'] = metrics.get_recent_activity(days=7)
        context['subject_performance'] = metrics.get_subject_performance()
        
        # Get linked parents
        context['linked_parents'] = student.get_linked_parents()
        
        # Get pending link requests from parents
        context['pending_requests'] = ParentStudent.objects.filter(
            student=student,
            status=ParentStudent.Status.PENDING
        ).select_related('parent')
        
        return context


class LinkRequestListView(StudentRequiredMixin, ListView):
    """View for students to see pending link requests from parents."""
    template_name = "students/link_requests.html"
    context_object_name = "link_requests"
    
    def get_queryset(self):
        return ParentStudent.objects.filter(
            student=self.request.user,
            status=ParentStudent.Status.PENDING
        ).select_related('parent').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Also show approved links
        context['approved_links'] = ParentStudent.objects.filter(
            student=self.request.user,
            status=ParentStudent.Status.APPROVED
        ).select_related('parent')
        return context


class LinkRequestActionView(StudentRequiredMixin, View):
    """View for students to approve or reject link requests."""
    
    def post(self, request, pk):
        link = get_object_or_404(
            ParentStudent.objects.select_related('parent'),
            pk=pk,
            student=request.user,
            status=ParentStudent.Status.PENDING
        )
        
        action = request.POST.get('action')
        
        if action == 'approve':
            link.approve()
            messages.success(
                request, 
                f"Permintaan dari {link.parent.get_full_name() or link.parent.username} disetujui."
            )
        elif action == 'reject':
            link.reject()
            messages.info(
                request, 
                f"Permintaan dari {link.parent.get_full_name() or link.parent.username} ditolak."
            )
        else:
            messages.error(request, "Aksi tidak valid.")
        
        return redirect('students:link_requests')


# ============================================================
# PARENT VIEWS (For users with role='parent')
# ============================================================

class ParentDashboardView(ParentRequiredMixin, TemplateView):
    """Dashboard view for parents."""
    template_name = "students/parent_dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.request.user
        
        # Get linked students (approved)
        students = User.objects.filter(
            parent_links__parent=parent,
            parent_links__status=ParentStudent.Status.APPROVED,
            role=User.Role.STUDENT
        ).order_by('grade', 'first_name')
        
        context['students'] = students
        context['students_count'] = students.count()
        
        # Get pending link requests
        context['pending_links'] = ParentStudent.objects.filter(
            parent=parent,
            status=ParentStudent.Status.PENDING
        ).count()
        
        # Get total quizzes taken by all linked students
        from apps.quizzes.models import QuizSession
        student_ids = students.values_list('pk', flat=True)
        
        sessions = QuizSession.objects.filter(
            student_id__in=student_ids,
            completed_at__isnull=False
        ).select_related('quiz', 'student').order_by('-completed_at')
        
        context['total_quizzes_taken'] = sessions.count()
        context['recent_sessions'] = sessions[:5]
        
        return context


class MyStudentsListView(ParentRequiredMixin, ListView):
    """View for parents to see their linked students."""
    template_name = "students/my_students.html"
    context_object_name = "students"
    
    def get_queryset(self):
        # Get all students linked to this parent (approved only)
        return User.objects.filter(
            parent_links__parent=self.request.user,
            parent_links__status=ParentStudent.Status.APPROVED,
            role=User.Role.STUDENT
        ).order_by('grade', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Also show pending link requests
        context['pending_links'] = ParentStudent.objects.filter(
            parent=self.request.user,
            status=ParentStudent.Status.PENDING
        ).select_related('student')
        return context


class StudentCreateByParentView(ParentRequiredMixin, CreateView):
    """View for parents to create a new student account."""
    form_class = CreateStudentForm
    template_name = "students/create_student.html"
    success_url = reverse_lazy("students:my_students")
    
    def form_valid(self, form):
        student = form.save(parent=self.request.user)
        messages.success(
            self.request, 
            f"Akun siswa {student.get_full_name()} berhasil dibuat dan terhubung."
        )
        return HttpResponseRedirect(self.success_url)


class StudentLinkView(ParentRequiredMixin, View):
    """View for parents to request link to an existing student."""
    template_name = "students/link_student.html"
    
    def get(self, request):
        form = LinkStudentForm()
        return self._render(request, form)
    
    def post(self, request):
        form = LinkStudentForm(request.POST)
        if form.is_valid():
            try:
                # Check if link already exists
                student = form.get_student()
                existing = ParentStudent.objects.filter(
                    parent=request.user,
                    student=student
                ).first()
                
                if existing:
                    if existing.status == ParentStudent.Status.PENDING:
                        messages.warning(request, "Permintaan sudah dikirim dan menunggu persetujuan siswa.")
                    elif existing.status == ParentStudent.Status.APPROVED:
                        messages.info(request, "Anda sudah terhubung dengan siswa ini.")
                    else:  # REJECTED
                        messages.error(request, "Permintaan sebelumnya ditolak oleh siswa.")
                    return redirect('students:my_students')
                
                # Create new link request
                link = form.save(parent=request.user)
                messages.success(
                    request, 
                    f"Permintaan link ke {student.get_full_name() or student.username} berhasil dikirim. "
                    "Menunggu persetujuan siswa."
                )
                return redirect('students:my_students')
                
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {str(e)}")
        
        return self._render(request, form)
    
    def _render(self, request, form):
        from django.shortcuts import render
        return render(request, self.template_name, {'form': form})


class ParentStudentDetailView(ParentRequiredMixin, DetailView):
    """View for parents to see detail of their linked student."""
    template_name = "students/student_detail.html"
    context_object_name = "student"
    
    def get_object(self):
        pk = self.kwargs['pk']
        # Ensure parent has access to this student
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        
        # Check if linked
        is_linked = ParentStudent.objects.filter(
            parent=self.request.user,
            student=student,
            status=ParentStudent.Status.APPROVED
        ).exists()
        
        if not is_linked:
            raise Http404("Siswa tidak ditemukan atau tidak terhubung dengan Anda.")
        
        return student
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get analytics for this student
        from apps.analytics.metrics import StudentMetrics
        metrics = StudentMetrics(student)
        
        context['total_attempts'] = metrics.get_total_attempts()
        context['accuracy'] = metrics.get_accuracy()
        context['total_xp'] = metrics.get_total_xp()
        context['recent_activity'] = metrics.get_recent_activity(days=7)
        context['subject_performance'] = metrics.get_subject_performance()
        context['strengths'] = metrics.get_strengths(min_attempts=1)
        context['weaknesses'] = metrics.get_weaknesses(min_attempts=1)
        
        return context


class SelectStudentForQuizView(ParentRequiredMixin, ListView):
    """View for parents to select a student before starting a proxy quiz."""
    template_name = "students/select_for_quiz.html"
    context_object_name = "students"
    
    def get_queryset(self):
        return User.objects.filter(
            parent_links__parent=self.request.user,
            parent_links__status=ParentStudent.Status.APPROVED,
            role=User.Role.STUDENT
        ).order_by('grade', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass quiz_id if provided
        context['quiz_id'] = self.request.GET.get('quiz_id')
        return context


class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating student profile (by student or parent)."""
    form_class = StudentProfileUpdateForm
    template_name = "students/profile_edit.html"
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        
        if pk:
            # Parent editing their student's profile
            student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
            
            # Verify parent has access
            if self.request.user.role == User.Role.PARENT:
                is_linked = ParentStudent.objects.filter(
                    parent=self.request.user,
                    student=student,
                    status=ParentStudent.Status.APPROVED
                ).exists()
                if not is_linked:
                    raise Http404("Tidak memiliki akses ke profil siswa ini.")
            elif self.request.user != student:
                raise Http404("Tidak memiliki akses.")
            
            return student
        else:
            # Student editing their own profile
            if self.request.user.role != User.Role.STUDENT:
                raise Http404("Halaman ini hanya untuk siswa.")
            return self.request.user
    
    def get_success_url(self):
        if self.request.user.role == User.Role.PARENT:
            return reverse('students:parent_student_detail', kwargs={'pk': self.object.pk})
        return reverse('students:dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, "Profil berhasil diperbarui.")
        return super().form_valid(form)


# ============================================================
# DEPRECATED VIEWS (Using old Student model)
# Kept for backward compatibility
# ============================================================

def _get_deprecated_student_list_view():
    """Factory function for deprecated StudentListView."""
    from .models import Student
    
    class StudentListView(ParentOrAdminMixin, ListView):
        """DEPRECATED: Use MyStudentsListView instead."""
        model = Student
        template_name = "students/list.html"
        context_object_name = "students"
        paginate_by = 20

        def get_queryset(self):
            queryset = Student.objects.select_related('parent')
            
            grade = self.request.GET.get('grade')
            if grade:
                queryset = queryset.filter(grade=grade)
                
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(name__icontains=search)
                
            return queryset.order_by('grade', 'name')
    
    return StudentListView


# Create deprecated views
StudentListView = _get_deprecated_student_list_view()
