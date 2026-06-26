from django.contrib import admin
from .models import EducationLevel, Grade, AcademicYear, GradeSubject, Enrollment


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "order")
    inlines = [GradeInline]


class GradeSubjectInline(admin.TabularInline):
    model = GradeSubject
    extra = 1
    autocomplete_fields = ["subject"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("label", "level", "number", "order")
    list_filter = ("level",)
    search_fields = ("label",)
    inlines = [GradeSubjectInline]


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(GradeSubject)
class GradeSubjectAdmin(admin.ModelAdmin):
    list_display = ("grade", "subject", "order")
    list_filter = ("grade__level", "grade")
    autocomplete_fields = ["subject"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "grade", "academic_year", "status", "created_at")
    list_filter = ("status", "academic_year", "grade__level")
    search_fields = ("student__username", "student__first_name", "student__last_name")
    autocomplete_fields = ["student", "grade"]
