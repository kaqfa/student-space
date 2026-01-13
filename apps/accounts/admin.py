from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ParentStudent

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'grade', 'is_active')
    list_filter = ('role', 'is_active', 'grade', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('role', 'username')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'grade', 'avatar', 'phone_number', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'grade', 'email', 'first_name', 'last_name')}),
    )

@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('parent__username', 'student__username', 'parent__email')
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status=ParentStudent.Status.APPROVED)
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status=ParentStudent.Status.REJECTED)
    reject_requests.short_description = "Reject selected requests"
