"""
AJAX view to save individual quiz answer.
Auto-save functionality for better UX.
"""
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.analytics.models import Attempt
from apps.quizzes.models import QuizSession
from apps.questions.models import Question


class SaveAnswerView(LoginRequiredMixin, View):
    """Save individual answer via AJAX."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            session_id = request.POST.get('session_id')
            question_id = request.POST.get('question_id')
            answer_given = request.POST.get('answer', '').strip().upper()
            
            # Get session and question
            session = QuizSession.objects.get(pk=session_id, completed_at__isnull=True)
            question = Question.objects.get(pk=question_id)
            
            # Verify question is in session
            if not session.session_questions.filter(pk=question_id).exists():
                return JsonResponse({'success': False, 'error': 'Question not in session'}, status=400)
            
            # Get or create attempt
            attempt, created = Attempt.objects.get_or_create(
                student=session.student,
                question=question,
                quiz_session=session,
                defaults={'answer_given': answer_given, 'is_correct': False}
            )
            
            # Update answer if already exists
            if not created:
                attempt.answer_given = answer_given
                
            # Check if correct
            if question.question_type == 'pilgan':
                attempt.is_correct = (answer_given == question.answer_key)
            
            attempt.save()
            
            return JsonResponse({
                'success': True,
                'answer_saved': answer_given,
                'is_correct': attempt.is_correct,
                'created': created
            })
            
        except QuizSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
