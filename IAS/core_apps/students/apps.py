from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IAS.core_apps.students"
    verbose_name = _("Student")
    verbose_name_plural = _("Students")
