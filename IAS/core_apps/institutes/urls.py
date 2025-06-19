from django.urls import path

from IAS.core_apps.institutes import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="InstituteDashboard"),
    path('department/create_read/', views.create_read_department, name="CreateReadDepartment"),
    path('designation/create_read/', views.create_read_designation, name="CreateReadDesignation"),
    path('staff/create_read/', views.create_read_staff, name="CreateReadStaff"),
    path('student/create_read/', views.create_read_student, name="CreateReadStudent"),
    path(
        'academic/class-section/create_read/',
        views.create_read_academic_class_section,
        name="CreateReadAcademicClassSection"
    ),
    path('academic/session/create_read/', views.create_read_academic_session, name="CreateReadAcademicSession"),
    path('academic/Info/create_read/', views.create_read_academic_info, name="CreateReadAcademicInfo"),
    path('academic/Info/delete/', views.delete_academic_info, name="DeleteAcademicInfo"),
    path('train/data/', views.train_model, name="InstituteTrainModel"),
]
