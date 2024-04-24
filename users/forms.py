from django import forms
from .models import UniversityUser, Department, WorkCategory, Requirement


class DepartmentAdminCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=12)

    department_name = forms.CharField(max_length=100)
    department_description = forms.CharField(widget=forms.Textarea, required=False)
    department_code = forms.CharField(max_length=150)


class DepartmentUserCreationForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    birthdate = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = UniversityUser
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "department",
            "birthdate",
        ]
        widgets = {"password": forms.PasswordInput()}


class WorkCategoryCreationForm(forms.ModelForm):
    class Meta:
        model = WorkCategory
        fields = ["name", "description", "max_percentage"]


class RequirementCreationForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ["work_category", "name", "description", "max_percentage_increase"]
