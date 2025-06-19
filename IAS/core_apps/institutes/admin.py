from django.contrib import admin

from .models import AcademicClassSection, AcademicSession, Department, Institute

# Register your models here.
admin.site.register(Institute)
admin.site.register(Department)
admin.site.register(AcademicSession)
admin.site.register(AcademicClassSection)
