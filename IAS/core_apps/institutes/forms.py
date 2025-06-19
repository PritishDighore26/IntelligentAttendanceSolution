from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction

from IAS.core_apps.common.models import RoleType
from IAS.core_apps.staffs.models import Staff
from IAS.core_apps.students.models import AcademicInfo, Student
from IAS.core_apps.users.models import Role

from .models import AcademicClassSection, AcademicSession, Department, Designation

AUTH_USER = get_user_model()


class DepartmentForm(forms.Form):
    department_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "department_name"
        }),
    )

    def save(self, institute):
        department_name = self.cleaned_data["department_name"]
        department = Department.is_department_exists(department_name, institute)

        if department:
            return False, "Department already exists!"

        try:

            Department.objects.create(department_name=department_name, institute=institute)

            return True, "Department created successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"


class DesignationForm(forms.Form):
    designation_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "designation_name"
        }),
    )

    def save(self, institute):
        designation_name = self.cleaned_data["designation_name"]
        designation = Designation.is_designation_exists(designation_name, institute)

        if designation:
            return False, "Designation already exists!"

        try:

            Designation.objects.create(designation_name=designation_name, institute=institute)

            return True, "Designation created successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"


class StaffForm(forms.Form):
    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "first_name"
        }),
    )
    last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "last_name"
        }),
    )
    email = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "email"
        }),
    )
    password = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "password"
        }),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "department"
        }),
        empty_label="Select Department",
    )
    designation = forms.ModelChoiceField(
        queryset=Designation.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "designation"
        }),
        empty_label="Select Designation",
    )

    def __init__(self, *args, **kwargs):
        self.institute = kwargs.pop("institute", None)  # Extract the 'institute' argument
        super().__init__(*args, **kwargs)  # Call the parent class initializer

        if self.institute:
            self.fields["department"].queryset = Department.objects.filter(is_deleted=False, institute=self.institute)
            self.fields["designation"].queryset = Designation.objects.filter(is_deleted=False, institute=self.institute)

    def save(self):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        department = self.cleaned_data["department"]
        designation = self.cleaned_data["designation"]

        try:
            with transaction.atomic():

                # Create the User
                user = AUTH_USER.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                )
                # Create the Role
                role = Role.objects.create(user=user, institute=self.institute, role_type=RoleType.STAFF)

                # Create the Staff
                Staff.objects.create(
                    role=role,
                    department=department,
                    designation=designation,
                    institute=self.institute,
                )

            return True, "Staff created successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"


class StudentForm(forms.Form):
    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "first_name"
        }),
    )
    last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "last_name"
        }),
    )
    email = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "email"
        }),
    )
    password = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "password"
        }),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "department"
        }),
        empty_label="Select Department",
    )
    enrollment = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "enrollment"
        }),
    )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        self.institute = self.current_user.institute
        super().__init__(*args, **kwargs)  # Call the parent class initializer

        if self.institute:
            self.fields["department"].queryset = Department.objects.filter(is_deleted=False, institute=self.institute)

    def save(self):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        department = self.cleaned_data["department"]
        enrollment = self.cleaned_data["enrollment"]

        try:
            with transaction.atomic():

                # Create the User
                user = AUTH_USER.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                )
                # Create the Role
                role = Role.objects.create(user=user, institute=self.institute, role_type=RoleType.STUDENT)
                created_by_uuid_role = f"{self.current_user.user.id}/{self.current_user.role_type}"

                # Create the Student
                Student.objects.create(
                    role=role,
                    department=department,
                    enrollment_number=enrollment,
                    institute=self.institute,
                    created_by_uuid_role=created_by_uuid_role
                )

            return True, "Student created successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"


class AcademicClassSectionForm(forms.Form):
    class_name = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "class_name"
        }),
    )
    section_name = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "section_name"
        }),
    )

    def save(self, institute):
        class_name = self.cleaned_data["class_name"]
        section_name = self.cleaned_data["section_name"]
        is_exists = AcademicClassSection.is_class_section_exists(class_name, section_name, institute)

        if is_exists:
            return False, "Academic Class Section already exists!"

        try:
            AcademicClassSection.objects.create(class_name=class_name, section_name=section_name, institute=institute)
            return True, "Academic Class Section created successfully"
        except Exception as e:
            return False, f"Something went wrong: {e}"


class AcademicSessionForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "start_date",
                "type": "date"  # Ensures the calendar popup is shown
            }
        ),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "end_date",
                "type": "date"  # Ensures the calendar popup is shown
            }
        ),
    )

    def save(self, institute):
        start_date = self.cleaned_data["start_date"]
        end_date = self.cleaned_data["end_date"]
        academic_session = AcademicSession.is_session_exists(start_date, end_date, institute)
        session_name = f"Session ({start_date} - {end_date})"
        if academic_session:
            return False, "Academic Session already exists!"

        try:

            AcademicSession.objects.create(
                session_name=session_name,
                start_date=start_date,
                end_date=end_date,
                institute=institute,
            )

            return True, "Academic Session created successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"


class AcademicInfoForm(forms.Form):

    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "student"
        }),
        empty_label="Select Student",
    )
    academic_class_section = forms.ModelChoiceField(
        queryset=AcademicClassSection.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "academic_class_section"
        }),
        empty_label="Select Class Section",
    )

    academic_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "academic_session"
        }),
        empty_label="Select Session",
    )

    def __init__(self, *args, **kwargs):
        self.institute = kwargs.pop("institute", None)
        super().__init__(*args, **kwargs)  # Call the parent class initializer

        if self.institute:
            self.fields["student"].queryset = Student.objects.filter(is_deleted=False, institute=self.institute)
            self.fields["academic_class_section"].queryset = AcademicClassSection.objects.filter(
                is_deleted=False, institute=self.institute
            )
            self.fields["academic_session"].queryset = AcademicSession.objects.filter(
                is_deleted=False, institute=self.institute
            )

    def save(self):
        student = self.cleaned_data["student"]
        academic_class_section = self.cleaned_data["academic_class_section"]
        academic_session = self.cleaned_data["academic_session"]
        try:

            AcademicInfo.objects.create(
                student=student,
                academic_class_section=academic_class_section,
                session=academic_session,
                institute=self.institute
            )

            return True, "Class-Section alloted successfully"

        except Exception as e:
            return False, f"Something went wrong: {e}"
