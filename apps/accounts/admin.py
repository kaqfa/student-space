from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, ParentStudent, Family, FamilyMembership, ParentProfile, TutorProfile,
)

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
    list_display = ('parent', 'student', 'status', 'family', 'created_at')
    list_filter = ('status', 'family', 'created_at')
    search_fields = ('parent__username', 'student__username', 'parent__email')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status=ParentStudent.Status.APPROVED)
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.update(status=ParentStudent.Status.REJECTED)
    reject_requests.short_description = "Reject selected requests"


class FamilyMembershipInline(admin.TabularInline):
    model = FamilyMembership
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'member_count', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    autocomplete_fields = ['owner']
    inlines = [FamilyMembershipInline]

    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = 'Members'


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display = ('family', 'user', 'role_in_family', 'created_at')
    list_filter = ('role_in_family',)
    search_fields = ('family__name', 'user__username')
    autocomplete_fields = ['family', 'user']


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ['user']


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')
    search_fields = ('user__username', 'specialization')
    autocomplete_fields = ['user']
