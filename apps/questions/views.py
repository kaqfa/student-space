from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, FormView
from django.contrib import messages
import json

from apps.accounts.mixins import PengajarOrAdminMixin
from .forms import QuestionForm, QuestionImportForm
from .models import Question, Tag, KompetensiDasar

from apps.subjects.models import Subject
from .services import import_questions_from_json


class QuestionListView(PengajarOrAdminMixin, ListView):
    model = Question
    template_name = "questions/list.html"
    context_object_name = "questions"
    paginate_by = 20

    def get_queryset(self):
        queryset = Question.objects.select_related(
            "topic", "topic__subject", "created_by"
        ).prefetch_related("tags", "kompetensi_dasar")
        
        subject_id = self.request.GET.get("subject")
        if subject_id:
            queryset = queryset.filter(topic__subject_id=subject_id)
            
        topic_id = self.request.GET.get("topic")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
            
        grade = self.request.GET.get("grade")
        if grade:
            queryset = queryset.filter(topic__subject__grade=grade)
            
        difficulty = self.request.GET.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        tags = self.request.GET.getlist("tags")
        if tags:
            queryset = queryset.filter(tags__id__in=tags)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all().order_by('name')
        return context


class QuestionDetailView(PengajarOrAdminMixin, DetailView):
    model = Question
    template_name = "questions/detail.html"
    context_object_name = "question"
    
    def get_queryset(self):
         return Question.objects.select_related(
            "topic", "topic__subject", "created_by"
        ).prefetch_related("tags", "kompetensi_dasar")


class QuestionCreateView(PengajarOrAdminMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "questions/form.html"
    success_url = reverse_lazy("questions:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Soal berhasil dibuat!")
        return super().form_valid(form)


class QuestionUpdateView(PengajarOrAdminMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = "questions/form.html"
    success_url = reverse_lazy("questions:list")
    
    def form_valid(self, form):
        messages.success(self.request, "Soal berhasil diperbarui!")
        return super().form_valid(form)


class QuestionDeleteView(PengajarOrAdminMixin, DeleteView):
    model = Question
    template_name = "questions/confirm_delete.html"
    success_url = reverse_lazy("questions:list")
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Soal berhasil dihapus!")
        return super().delete(request, *args, **kwargs)


class QuestionImportView(PengajarOrAdminMixin, FormView):
    template_name = "questions/import.html"
    form_class = QuestionImportForm
    success_url = reverse_lazy("questions:list")
    
    def form_valid(self, form):
        file = form.cleaned_data['file']
        try:
            data = json.load(file)
            count, errors = import_questions_from_json(data, user=self.request.user)
            
            if count > 0:
                messages.success(self.request, f"Successfully imported {count} questions.")
            
            if errors:
                for err in errors[:5]: # Show first 5 errors only
                     messages.warning(self.request, err)
                if len(errors) > 5:
                     messages.warning(self.request, f"And {len(errors) - 5} more errors.")
            
            if count == 0 and not errors:
                 messages.info(self.request, "No questions found in JSON.")

        except json.JSONDecodeError:
            messages.error(self.request, "Invalid JSON file.")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Import failed: {str(e)}")
            return self.form_invalid(form)
            
        return super().form_valid(form)

# --- Tag Views ---

class TagListView(PengajarOrAdminMixin, ListView):
    model = Tag
    template_name = "questions/tag_list.html"
    context_object_name = "tags"
    paginate_by = 50

class TagCreateView(PengajarOrAdminMixin, CreateView):
    model = Tag
    fields = ["name"]
    template_name = "questions/tag_form.html"
    success_url = reverse_lazy("questions:tag-list") # Need url update

    def form_valid(self, form):
        messages.success(self.request, "Tag berhasil dibuat.")
        return super().form_valid(form)

class TagUpdateView(PengajarOrAdminMixin, UpdateView):
    model = Tag
    fields = ["name"]
    template_name = "questions/tag_form.html"
    success_url = reverse_lazy("questions:tag-list")

class TagDeleteView(PengajarOrAdminMixin, DeleteView):
    model = Tag
    template_name = "questions/tag_confirm_delete.html"
    success_url = reverse_lazy("questions:tag-list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tag berhasil dihapus.")
        return super().delete(request, *args, **kwargs)

# --- Kompetensi Dasar Views ---

class KDListView(PengajarOrAdminMixin, ListView):
    model = KompetensiDasar
    template_name = "questions/kd_list.html"
    context_object_name = "kds"
    paginate_by = 50

    def get_queryset(self):
        return KompetensiDasar.objects.select_related('subject')

class KDCreateView(PengajarOrAdminMixin, CreateView):
    model = KompetensiDasar
    fields = ["subject", "grade", "code", "description"]
    template_name = "questions/kd_form.html"
    success_url = reverse_lazy("questions:kd-list")

    def form_valid(self, form):
        messages.success(self.request, "KD berhasil dibuat.")
        return super().form_valid(form)

class KDUpdateView(PengajarOrAdminMixin, UpdateView):
    model = KompetensiDasar
    fields = ["subject", "grade", "code", "description"]
    template_name = "questions/kd_form.html"
    success_url = reverse_lazy("questions:kd-list")

class KDDeleteView(PengajarOrAdminMixin, DeleteView):
    model = KompetensiDasar
    template_name = "questions/kd_confirm_delete.html"
    success_url = reverse_lazy("questions:kd-list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "KD berhasil dihapus.")
        return super().delete(request, *args, **kwargs)
