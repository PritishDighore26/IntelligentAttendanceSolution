from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AttendanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IAS.core_apps.attendance"
    verbose_name = _("Attendance")
    verbose_name_plural = _("Attendances")
