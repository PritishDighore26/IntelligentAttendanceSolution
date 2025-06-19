from django.urls import path

from IAS.core_apps.students import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="StudentDashboard"),
    path(
        "attendance/create_read/",
        views.attendance_create_read,
        name="StudentAttendanceCreateRead",
    ),
]
