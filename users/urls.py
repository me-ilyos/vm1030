from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    create_department_user,
    department_list,
    create_department_admin,
    create_work_category,
    get_workcategories,
    get_workcategory_detail,
    WorkCategoryEditView
)

app_name = "users"

urlpatterns = [
    path("create_department/", create_department_admin, name="create_department"),
    path(
        "create_department_user/",
        create_department_user,
        name="create_department_user",
    ),
    path("departments/", department_list, name="department_list"),
    path("create_workcategory/", create_work_category, name="create_work_category"),
    path("work_categories/", get_workcategories, name="work_categories"),
    path('work-categories/<int:pk>/', get_workcategory_detail, name='workcategory_detail'),
    path('work-categories/<int:pk>/edit/', WorkCategoryEditView.as_view(), 
         name='workcategory_edit'),

    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
