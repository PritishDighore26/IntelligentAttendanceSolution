import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from IAS.core_apps.common.models import RoleType
from IAS.core_apps.institutes.models import Institute

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    # pseudo primary key to avoid disadvantage of uuid primary key
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # noqa: A003
    first_name = models.CharField(verbose_name=_("first name"), max_length=50)
    last_name = models.CharField(verbose_name=_("last name"), max_length=50)
    email = models.EmailField(
        verbose_name=_("email address"), db_index=True,
        unique=True)  # db_index to create indexing for email field

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_image_number = models.IntegerField(default=0)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return f"{self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def short_name(self):
        return self.first_name

    @property
    def role_data(self):
        return Role.objects.get(user=self)


class Role(models.Model):
    """
    Role Model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="institute_roles")
    role_type = models.CharField(max_length=10, choices=RoleType.choices, default=RoleType.STAFF)
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    class Meta:
        unique_together = ("user", "institute")

    def __str__(self) -> str:
        return f"{self.id} - {self.role_type}"
