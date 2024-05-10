from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"

urlpatterns = [
    path("create_department/", views.create_department_admin, name="create_department"),
    path(
        "create_department_user/",
        views.create_department_user,
        name="create_department_user",
    ),
    path("departments/", views.department_list, name="department_list"),
    path("create_workcategory/", views.create_work_category, name="create_work_category"),
    path("work_categories/", views.get_workcategories, name="work_categories"),
    path('work-categories/<int:pk>/', views.get_workcategory_detail, name='workcategory_detail'),
    path('work-categories/<int:pk>/edit/', views.WorkCategoryEditView.as_view(), 
         name='workcategory_edit'),
    path("work_submission/", views.submission_form_view, name="work_submission"),
    path("process_submission/", views.process_submission, name="process_submission"),
    path("processing_submissions/", views.list_processing_submissions, name="list_processing_submissions"),
    path('submission/<int:pk>/download/', views.download_submission, name='download_submission'),
    path('submission/<int:pk>/approve/', views.approve_submission, name='approve_submission'),
    path('submission/<int:pk>/decline/', views.decline_submission, name='decline_submission'), 
    path('submissions/approved/', views.department_approved_submissions, name='approved_submissions'),
    path('submissions/approved/<int:pk>/approve/', views.approve_submission_da, name='approve_submission_da'),
    path('submissions/approved/<int:pk>/decline/', views.decline_submission_da, name='decline_submission_da'),
    path('all_submissions/', views.all_submissions_list, name='all_submissions_list'),
    path('submissions/my-list/', views.my_submissions_list, name='my_submissions_list'),

    path('', views.admin_dashboard, name='admin_dashboard'),
    path('departments/<int:department_id>/', views.department_admin_dashboard, name='department_admin_dashboard'),
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
