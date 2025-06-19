from django.contrib import admin

from .models import AcademicInfo, Student

# Register your models here.
admin.site.register(Student)
admin.site.register(AcademicInfo)
