from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StaffsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "IAS.core_apps.staffs"
    verbose_name = _("Staff")
    verbose_name_plural = _("Staffs")
