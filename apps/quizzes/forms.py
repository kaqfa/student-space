from django import forms
from django.core.exceptions import ValidationError
from .models import Quiz
from apps.subjects.models import Subject
from apps.questions.models import Question

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'subject', 'grade', 'time_limit_minutes','passing_score', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'subject': forms.Select(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'grade': forms.NumberInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'passing_score': forms.NumberInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'}),
        }


class SubjectQuizForm(forms.ModelForm):
    """Form for creating subject-based quizzes with random questions."""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'subject', 'grade', 'question_count', 'time_limit_minutes', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Matematika Kelas 6 - Latihan Umum'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.Select(attrs={'class': 'form-select'}, choices=[(i, f'Kelas {i}') for i in range(1, 7)]),
            'question_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set quiz_type on initialization for new instances
        if not self.instance.pk:
            self.instance.quiz_type = Quiz.QuizType.SUBJECT_BASED
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ensure quiz_type is set (in case form was initialized differently)
        instance.quiz_type = Quiz.QuizType.SUBJECT_BASED
        if commit:
            instance.save()
        return instance


class CustomQuizBasicForm(forms.ModelForm):
    """Form for custom quiz basic info including question_count."""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'subject', 'grade', 'question_count', 'time_limit_minutes', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.Select(attrs={'class': 'form-select'}, choices=[(i, f'Kelas {i}') for i in range(1, 7)]),
            'question_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
        help_texts = {
            'question_count': 'Jumlah soal random dari yang dipilih (kosongkan untuk gunakan semua)',
        }
