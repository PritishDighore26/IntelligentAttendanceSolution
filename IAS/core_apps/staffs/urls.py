from django.urls import path

from IAS.core_apps.institutes import views as institutes_views
from IAS.core_apps.staffs import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="StaffDashboard"),
    path("profile/update_read/", views.profile, name="StaffProfileUpdateRead"),
    path(
        "student/create_read/",
        institutes_views.create_read_student,
        name="StaffCreateReadStudent",
    ),
]
