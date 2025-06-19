from django.contrib.auth import get_user_model
from django.db import models

from IAS.core_apps.common.models import BloodGroup, Gender, IASModel
from IAS.core_apps.institutes.models import AcademicClassSection, AcademicSession, Department, Institute
from IAS.core_apps.users.models import Role

AUTH_USER = get_user_model()


def student_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"{instance.institute.id}/{instance.id}/{filename}"


# Create your models here.
class Student(IASModel):
    role = models.OneToOneField(Role, on_delete=models.CASCADE, related_name="role_student")
    enrollment_number = models.CharField(max_length=100, unique=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="institute_student", null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="student_department",
        null=True,
    )
    created_by_uuid_role = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(
        blank=True,
        default="/profile_images/default_profile.png",
        upload_to=student_directory_path,
    )
    dob = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=400, null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_ANSWER,
    )
    blood_group = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=BloodGroup.choices,
        default=BloodGroup.OTHER,
    )
    mobile_no = models.CharField(max_length=16, null=True, blank=True)
    about = models.CharField(max_length=566, null=True, blank=True)

    def __str__(self):
        return f"{self.role.user.full_name} - Student"

    @property
    def created_by_name(self):
        created_name = ""
        if self.created_by_uuid_role and "/" in self.created_by_uuid_role:
            uuid, role = str(self.created_by_uuid_role).split("/")
            created_user = AUTH_USER.objects.get(id=uuid)
            created_name = (f"{created_user.first_name} {created_user.last_name} ({role})")
        return created_name


class AcademicInfo(IASModel):
    """
    AcademicSession model to store Institute Session
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_academic", null=True, blank=True
    )
    academic_class_section = models.ForeignKey(
        AcademicClassSection, on_delete=models.CASCADE, related_name="class_section_academic", null=True, blank=True
    )
    session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE, related_name="session_academic", null=True, blank=True
    )
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="institute_academic", null=True, blank=True
    )

    def __str__(self):
        return f"{self.student} - {self.institute.institute_name}"
