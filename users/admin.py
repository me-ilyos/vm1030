from django.contrib import admin
from .models import (
    UniversityUser,
    Department,
    DepartmentAdminProfile,
    DepartmentUserProfile,
    SuperAdminProfile,
    WorkCategory,
    ProfessorWorkSubmission,
    Requirement,
)

admin.site.register(DepartmentAdminProfile)
admin.site.register(UniversityUser)
admin.site.register(Department)
admin.site.register(DepartmentUserProfile)
admin.site.register(SuperAdminProfile)
admin.site.register(WorkCategory)
admin.site.register(ProfessorWorkSubmission)
admin.site.register(Requirement)
