import csv
from io import StringIO
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from datetime import datetime

from apps.analytics.models import Attempt
from apps.quizzes.models import QuizSession

User = get_user_model()


def generate_student_report_csv(student, date_from=None, date_to=None):
    """
    Generate a CSV report for a student's performance.
    Returns an HttpResponse with CSV content.
    
    Args:
        student: User instance with role='student'
        date_from: Optional start date filter
        date_to: Optional end date filter
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Get student name
    student_name = student.get_full_name() or student.username
    
    # Header
    writer.writerow([f'Laporan Progress Siswa: {student_name}'])
    writer.writerow([f'Kelas: {student.grade or "-"}'])
    writer.writerow([f'Tanggal Laporan: {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([])  # Empty row
    
    # Summary section
    writer.writerow(['=== RINGKASAN ==='])
    
    attempts = Attempt.objects.filter(student=student)
    if date_from:
        attempts = attempts.filter(created_at__gte=date_from)
    if date_to:
        attempts = attempts.filter(created_at__lte=date_to)
    
    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0
    total_points = sum(a.points_earned for a in attempts)
    
    writer.writerow(['Total Soal Dikerjakan', total_attempts])
    writer.writerow(['Jawaban Benar', correct_attempts])
    writer.writerow(['Akurasi', f'{accuracy}%'])
    writer.writerow(['Total Poin', total_points])
    writer.writerow([])
    
    # Quiz Summary
    writer.writerow(['=== STATISTIK KUIS ==='])
    sessions = QuizSession.objects.filter(student=student, completed_at__isnull=False)
    if date_from:
        sessions = sessions.filter(started_at__gte=date_from)
    if date_to:
        sessions = sessions.filter(started_at__lte=date_to)
    
    writer.writerow(['Kuis Dikerjakan', sessions.count()])
    writer.writerow(['Kuis Lulus', sessions.filter(passed=True).count()])
    writer.writerow([])
    
    # Attempt Details
    writer.writerow(['=== DETAIL JAWABAN ==='])
    writer.writerow(['Tanggal', 'Mata Pelajaran', 'Topik', 'Soal', 'Jawaban', 'Benar/Salah', 'Poin'])
    
    for attempt in attempts.select_related('question', 'question__topic', 'question__topic__subject').order_by('-created_at')[:100]:
        writer.writerow([
            attempt.created_at.strftime('%d/%m/%Y %H:%M'),
            attempt.question.topic.subject.name if attempt.question.topic else '-',
            attempt.question.topic.name if attempt.question.topic else '-',
            attempt.question.question_text[:50] + '...' if len(attempt.question.question_text) > 50 else attempt.question.question_text,
            attempt.answer_given or '-',
            'Benar' if attempt.is_correct else 'Salah',
            attempt.points_earned,
        ])
    
    # Create response
    output.seek(0)
    response = HttpResponse(output.read(), content_type='text/csv')
    filename = f'laporan_{student_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def generate_class_summary_csv(grade=None):
    """
    Generate a CSV summary of all students (optionally filtered by grade).
    Uses User model with role='student'.
    """
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([f'Ringkasan Kelas{" - Kelas " + str(grade) if grade else ""}'])
    writer.writerow([f'Tanggal: {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([])
    
    writer.writerow(['Nama Siswa', 'Kelas', 'Total Soal', 'Benar', 'Akurasi', 'Total Poin', 'Kuis Lulus'])
    
    students = User.objects.filter(role=User.Role.STUDENT)
    if grade:
        students = students.filter(grade=grade)
    
    for student in students.order_by('grade', 'first_name'):
        student_name = student.get_full_name() or student.username
        attempts = Attempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        accuracy = round((correct / total) * 100, 1) if total > 0 else 0
        points = sum(a.points_earned for a in attempts)
        quizzes_passed = QuizSession.objects.filter(
            student=student, 
            completed_at__isnull=False, 
            passed=True
        ).count()
        
        writer.writerow([
            student_name,
            student.grade or '-',
            total,
            correct,
            f'{accuracy}%',
            points,
            quizzes_passed,
        ])
    
    output.seek(0)
    response = HttpResponse(output.read(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ringkasan_kelas_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    return response
