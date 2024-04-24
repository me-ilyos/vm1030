from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.forms.models import inlineformset_factory

from .models import (
    Department,
    UniversityUser,
    DepartmentUserProfile,
    WorkCategory,
    Requirement,
)
from .forms import (
    DepartmentAdminCreationForm,
    DepartmentUserCreationForm,
    WorkCategoryCreationForm,
    RequirementCreationForm,
    WorkCategoryEditForm, 
    RequirementEditFormset
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


@user_passes_test(is_superadmin)
def create_work_category(request):
    if request.method == "POST":
        category_form = WorkCategoryCreationForm(request.POST)
        requirement_formset = RequirementFormset(
            request.POST, instance=category_form.instance
        )
        if category_form.is_valid() and requirement_formset.is_valid():
            category_form.save()
            requirement_formset.save()
            return redirect("users:department_list")
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
