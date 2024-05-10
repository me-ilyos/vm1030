from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.forms.models import inlineformset_factory
from django.utils.text import slugify
from io import BytesIO
from zipfile import ZipFile
from django.contrib.auth.decorators import login_required

from .models import (
    Department,
    UniversityUser,
    DepartmentUserProfile,
    WorkCategory,
    Requirement,
    ProfessorWorkSubmission,
    FileSubmission
)
from .forms import (
    DepartmentAdminCreationForm,
    DepartmentUserCreationForm,
    WorkCategoryCreationForm,
    RequirementCreationForm,
    WorkCategoryEditForm, 
    RequirementEditFormset,
)


def is_superadmin(user):
    return user.is_superuser


def is_department_admin(user):
    return user.role == "DA"


RequirementFormset = inlineformset_factory(
    WorkCategory,
    Requirement,
    fields=["name", "description", "max_percentage_increase"],
    extra=4,
)


@user_passes_test(is_superadmin)
def create_department_admin(request):
    if request.method == "POST":
        form = DepartmentAdminCreationForm(request.POST)
        if form.is_valid():

            user = UniversityUser.objects.create(
                username=form.cleaned_data["username"],
                phone_number=form.cleaned_data["phone_number"],
                password=make_password(form.cleaned_data["password"]),
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                role="DA",
            )
            user.save()

            department = Department.objects.create(
                name=form.cleaned_data["department_name"],
                description=form.cleaned_data["department_description"],
                code=form.cleaned_data["department_code"],
                department_admin=user,
            )
            department.save()

            return redirect("users:department_list")
    else:
        form = DepartmentAdminCreationForm()
    return render(request, "users/create_department.html", {"form": form})


@user_passes_test(is_superadmin)
def department_list(request):
    departments = Department.objects.all()
    context = {"departments": departments}
    return render(request, "users/department_list.html", context)


# @user_passes_test(is_department_admin)
def create_department_user(request):
    if request.method == "POST":
        form = DepartmentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "DU"
            user.set_password(form.cleaned_data["password"])
            user.save()

            DepartmentUserProfile.objects.create(
                user=user,
                birthdate=form.cleaned_data["birthdate"],
                department=form.cleaned_data["department"],
            )

            return redirect("users:department_list")
    else:
        form = DepartmentUserCreationForm()
    return render(request, "users/create_department_user.html", {"form": form})


# @user_passes_test(is_superadmin)
def create_work_category(request):
    if request.method == "POST":
        category_form = WorkCategoryCreationForm(request.POST)
        requirement_formset = RequirementFormset(
            request.POST, instance=category_form.instance
        )
        print(requirement_formset)
        if category_form.is_valid() and requirement_formset.is_valid():
            print("FORM IS VALID")
            category_form.save()
            requirement_formset.save()
            return redirect("users:admin_dashboard")
    else:
        category_form = WorkCategoryCreationForm()
        requirement_formset = RequirementFormset()
    return render(
        request,
        "users/create_workcategory.html",
        {"category_form": category_form, "requirement_formset": requirement_formset},
    )


def get_workcategories(request):
    work_categories = WorkCategory.objects.prefetch_related('requirements')
    context = {'work_categories': work_categories}
    return render(request, 'users/get_workcategories.html', context)


def get_workcategory_detail(request, pk):
    work_category = get_object_or_404(WorkCategory, pk=pk)
    context = {'work_category': work_category}

    return render(request, 'users/workcategory_detail.html', context)


class WorkCategoryEditView(UpdateView):
    model = WorkCategory
    template_name = 'users/workcategory_edit.html'
    form_class = WorkCategoryEditForm
    success_url = reverse_lazy('users:work_categories')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['requirement_formset'] = RequirementFormset(self.request.POST, instance=self.object)
        else:
            ctx['requirement_formset'] = RequirementFormset(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['requirement_formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
        
    
def submission_form_view(request):
    categories = WorkCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'users/work_submission.html', context)


def process_submission(request):
     if request.method == 'POST':
        category_id = request.POST.get('category_id')  

        if not category_id:
            raise Http404("Category ID not found.")

        category = get_object_or_404(WorkCategory, pk=category_id)
        professor = request.user

        submission = ProfessorWorkSubmission.objects.create(
            professor=professor,
            work_category=category 
        )

        for key, file in request.FILES.items():
            print(f"Key: {key}", file)
            if key.startswith('requirement_'):
                requirement_id = key.split('_')[1]
                try:
                    requirement = Requirement.objects.get(id=requirement_id)
                    FileSubmission.objects.create(
                        proof_file=file,
                        requirement=requirement,
                        work_submission=submission 
                    ).save()
                    submission.requirements.add(requirement)
                except Requirement.DoesNotExist:
                    print("-----------------Requirement.DoesNotExist------------------")

        submission.save()
        return redirect('users:work_categories')
     

def list_processing_submissions(request):
    processing_submissions = ProfessorWorkSubmission.objects.filter(status="PR").select_related('professor', 'work_category')

    context = {
        'submissions': processing_submissions,
    }
    return render(request, 'users/processing_submissions_list.html', context)


def download_submission(request, pk):
    submission = get_object_or_404(ProfessorWorkSubmission, pk=pk)

    response = HttpResponse(content_type='application/zip')
    zip_filename = f"{slugify(submission)}-files.zip"  
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"' 

    with ZipFile(response, 'w') as zip_file:
        for file_submission in submission.file_submissions.all():
            print(file_submission.proof_file.path)
            with file_submission.proof_file.open('rb') as file:
                zip_file.writestr(file_submission.proof_file.name, file.read())

    return response


def approve_submission(request, pk):
    submission = get_object_or_404(ProfessorWorkSubmission, pk=pk)
    if submission.status == "PR":
        submission.status = "DA"
        submission.save()
    return redirect("users:list_processing_submissions")


def decline_submission(request, pk):
    submission = get_object_or_404(ProfessorWorkSubmission, pk=pk)
    if submission.status == "PR":
        submission.status = "DN" 
        submission.save()
    return redirect("users:list_processing_submissions")


def department_approved_submissions(request):
    approved_submissions = ProfessorWorkSubmission.objects.filter(status="DA")
    context = {'submissions': approved_submissions}
    return render(request, 'users/department_approved_submissions.html', context)


def approve_submission_da(request, pk):
    submission = get_object_or_404(ProfessorWorkSubmission, pk=pk)
    if submission.status == "DA":
        submission.status = "SA"
        submission.save()
    return redirect("users:approved_submissions")


def decline_submission_da(request, pk):
    submission = get_object_or_404(ProfessorWorkSubmission, pk=pk)
    if submission.status == "DA":
        submission.status = "PR"
        submission.save()
    return redirect("users:approved_submissions")


@login_required  
def all_submissions_list(request):
    submissions = ProfessorWorkSubmission.objects.all().select_related('professor', 'work_category').order_by('-created_at')
    context = {
        'submissions': submissions
    }
    return render(request, 'users/all_submissions_list.html', context)


class MyLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('users:admin_dashboard') 
        elif self.request.user.role == "DA":
            print("We are here")
            department = self.request.user.admin_of_department 
            print(department.pk)
            return redirect('users:department_admin_dashboard', department_id=int(4))

@login_required
def admin_dashboard(request):
    context = {"is_admin": True}
    return render(request, 'users/admin_dashboard.html', context)


def department_admin_dashboard(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    context = {
        'department': department,
    }
    return render(request, 'department_admin_dashboard.html', context)


def my_submissions_list(request):
    user = get_object_or_404(UniversityUser, pk=request.user.pk)
    submissions = ProfessorWorkSubmission.objects.filter(professor=user).order_by('-created_at')
    context = {'submissions': submissions}
    return render(request, 'users/my_submissions_list.html', context)
