from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import ParentStudent

User = get_user_model()

# Common Tailwind CSS classes for form inputs
INPUT_CLASS = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
TEXTAREA_CLASS = 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
CHECKBOX_CLASS = 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
FILE_CLASS = 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
SELECT_CLASS = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'


class StudentRegistrationForm(forms.ModelForm):
    """
    Form for student self-registration.
    Creates a User with role='student' and sets grade/date_of_birth on User model.
    """
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'username'})
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'email@example.com'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': '********'})
    )
    confirm_password = forms.CharField(
        label=_("Konfirmasi Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': '********'})
    )
    first_name = forms.CharField(
        label=_("Nama Depan"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    last_name = forms.CharField(
        label=_("Nama Belakang"),
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    grade = forms.IntegerField(
        label=_("Kelas (1-6)"),
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 6})
    )
    date_of_birth = forms.DateField(
        label=_("Tanggal Lahir"),
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Password tidak cocok."))
        
        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email sudah terdaftar."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.STUDENT
        user.grade = self.cleaned_data["grade"]
        user.date_of_birth = self.cleaned_data.get("date_of_birth")
        
        if commit:
            user.save()
        return user


class ParentRegistrationForm(forms.ModelForm):
    """
    Form for parent registration.
    Creates a User with role='parent'.
    """
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'username'})
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'email@example.com'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': '********'})
    )
    confirm_password = forms.CharField(
        label=_("Konfirmasi Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': '********'})
    )
    first_name = forms.CharField(
        label=_("Nama Depan"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    last_name = forms.CharField(
        label=_("Nama Belakang"),
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    phone = forms.CharField(
        label=_("Nomor Telepon"),
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '08xxxxxxxxxx'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Password tidak cocok."))
        
        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email sudah terdaftar."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.PARENT
        
        if commit:
            user.save()
        return user


class CreateStudentForm(forms.ModelForm):
    """
    Form for parent to create a new student account.
    The created student will be automatically linked to the parent.
    """
    username = forms.CharField(
        label=_("Username untuk siswa"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS})
    )
    confirm_password = forms.CharField(
        label=_("Konfirmasi Password"),
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS})
    )
    first_name = forms.CharField(
        label=_("Nama Depan Siswa"),
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    last_name = forms.CharField(
        label=_("Nama Belakang Siswa"),
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    grade = forms.IntegerField(
        label=_("Kelas (1-6)"),
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 6})
    )
    date_of_birth = forms.DateField(
        label=_("Tanggal Lahir"),
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'})
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Password tidak cocok."))

        return cleaned_data

    def save(self, parent, commit=True):
        """
        Save the student and create ParentStudent link.
        
        Args:
            parent: The parent User creating this student
            commit: Whether to save to database
        
        Returns:
            The created student User
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.STUDENT
        user.grade = self.cleaned_data["grade"]
        user.date_of_birth = self.cleaned_data.get("date_of_birth")
        
        if commit:
            user.save()
            # Create auto-approved link
            ParentStudent.create_with_new_student(parent=parent, student=user)
        
        return user


class LinkStudentForm(forms.Form):
    """
    Form for parent to request link to an existing student.
    The student will need to approve this request.
    """
    student_username = forms.CharField(
        label=_("Username Siswa"),
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Masukkan username siswa'
        }),
        help_text=_("Masukkan username akun siswa yang ingin dihubungkan")
    )
    notes = forms.CharField(
        label=_("Catatan (opsional)"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': TEXTAREA_CLASS,
            'rows': 3,
            'placeholder': 'Pesan untuk siswa, misal: "Saya adalah orang tua kamu"'
        }),
        help_text=_("Catatan ini akan dilihat oleh siswa saat menyetujui permintaan")
    )

    def clean_student_username(self):
        username = self.cleaned_data["student_username"]
        try:
            student = User.objects.get(username=username, role=User.Role.STUDENT)
        except User.DoesNotExist:
            raise forms.ValidationError(_("Siswa dengan username tersebut tidak ditemukan."))
        return username

    def get_student(self):
        """Get the student User object."""
        username = self.cleaned_data["student_username"]
        return User.objects.get(username=username, role=User.Role.STUDENT)

    def save(self, parent):
        """
        Create a pending ParentStudent link request.
        
        Args:
            parent: The parent User making the request
        
        Returns:
            The created ParentStudent object
        """
        student = self.get_student()
        notes = self.cleaned_data.get("notes", "")
        return ParentStudent.request_link(parent=parent, student=student, notes=notes)


class StudentProfileUpdateForm(forms.ModelForm):
    """
    Form for updating student profile (by student themselves or parent).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'grade', 'date_of_birth', 'avatar', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'grade': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'max': 6}),
            'date_of_birth': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': FILE_CLASS}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }


# ============================================================
# DEPRECATED: Old forms using Student model
# Kept for backward compatibility during migration
# ============================================================

class StudentUpdateForm(forms.ModelForm):
    """
    DEPRECATED: Use StudentProfileUpdateForm instead.
    This form uses the old Student model.
    """
    class Meta:
        from .models import Student
        model = Student
        fields = ['name', 'grade', 'date_of_birth', 'notes', 'is_active', 'avatar', 'pengajar']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'grade': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}),
            'avatar': forms.FileInput(attrs={'class': FILE_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'pengajar': forms.CheckboxSelectMultiple(),
        }
