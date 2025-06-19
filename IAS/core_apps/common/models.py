import uuid

from django.db import models


# This model is abstract model which will be inherit by other models across all the core apps
class IASModel(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]


class RoleType(models.TextChoices):
    OWNER = "owner", "Owner"
    STAFF = "staff", "Staff"
    STUDENT = "student", "Student"
    ANONYMOUS = "anonymous", "Anonymous"


ROLE_URL_MAP = {
    RoleType.OWNER: "InstituteDashboard",
    RoleType.STAFF: "StaffDashboard",
    RoleType.STUDENT: "StudentDashboard",
    RoleType.ANONYMOUS: "Login",
}

STUDENT_CRUD_URL_MAP = {
    RoleType.OWNER: "CreateReadStudent",
    RoleType.STAFF: "StaffCreateReadStudent",
}


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    ON_LEAVE = "on leave", "On Leave"
    HOLIDAY = "holiday", "Holiday"
    WEEKEND = "weekend", "Weekend"


class BloodGroup(models.TextChoices):
    A_POSITIVE = "A+", "A+"
    B_POSITIVE = "B+", "B+"
    AB_POSITIVE = "AB+", "AB+"
    O_POSITIVE = "O+", "O+"
    A_NEGATIVE = "A-", "A-"
    B_NEGATIVE = "B-", "B-"
    AB_NEGATIVE = "AB-", "AB-"
    O_NEGATIVE = "O-", "O-"
    OTHER = "Other", "Other"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    TRANSGENDER = "transgender", "Transgender"
    PREFER_NOT_TO_ANSWER = "prefer not to answer", "Prefer not to answer"
