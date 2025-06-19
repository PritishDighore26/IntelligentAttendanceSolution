from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from IAS.core_apps.attendance.models import Attendance
from IAS.core_apps.common.decorators import allowed_users
from IAS.core_apps.common.models import ROLE_URL_MAP, STUDENT_CRUD_URL_MAP, AttendanceStatus, RoleType
from IAS.core_apps.institutes.forms import (
    AcademicClassSectionForm, AcademicInfoForm, AcademicSessionForm, DepartmentForm, DesignationForm, StaffForm,
    StudentForm
)
from IAS.core_apps.institutes.models import AcademicClassSection, AcademicSession, Department, Designation
from IAS.core_apps.staffs.models import Staff
from IAS.core_apps.students.models import AcademicInfo, Student
from IAS.scripts.train_face_recognization_model import start_training


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def dashboard(request):
    institute = request.user.role_data.institute
    student_count = Student.objects.filter(institute=institute, is_deleted=False).count()
    staff_count = Staff.objects.filter(institute=institute, is_deleted=False).count()
    todays_date = date.today()
    todays_attendance = Attendance.objects.filter(
        institute=institute,
        is_deleted=False,
        a_date=todays_date,
    )
    present_count = todays_attendance.filter(a_status=AttendanceStatus.PRESENT).count()
    absent_count = todays_attendance.filter(a_status__in=[AttendanceStatus.ABSENT]).count()
    yesterday = todays_date - timedelta(days=7)
    recent_activities = Attendance.objects.filter(
        institute=institute,
        is_deleted=False,
        a_date__gte=yesterday,
    )
    context = {
        "student_count": student_count,
        "staff_count": staff_count,
        "present_count": present_count,
        "absent_count": absent_count,
        "todays_attendance": todays_attendance,
        "recent_activities": recent_activities,
    }
    return render(request, "institutes/dashboard.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_department(request):
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save(session_institute)
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadDepartment"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadDepartment"))
    else:
        form = DepartmentForm()
    departments = Department.objects.filter(institute=session_institute).order_by("pkid")
    context = {"form": form, "departments": departments}
    return render(request, "institutes/manage_department/department.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_designation(request):
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = DesignationForm(request.POST)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save(session_institute)
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadDesignation"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadDesignation"))
    else:
        form = DesignationForm()
    designations = Designation.objects.filter(institute=session_institute).order_by("pkid")
    context = {"form": form, "designations": designations}
    return render(request, "institutes/manage_designation/designation.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_staff(request):
    state = False
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = StaffForm(request.POST, institute=session_institute)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save()
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadStaff"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadStaff"))
    else:
        form = StaffForm(institute=session_institute)
    staffs = Staff.objects.filter(institute=session_institute).order_by("pkid")
    context = {"form": form, "staffs": staffs, "state": state}
    return render(request, "institutes/manage_staff/staff.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER, RoleType.STAFF])
def create_read_student(request):
    current_user = request.user.role_data
    state = False
    # session_institute is the logged in user's institute
    session_institute = current_user.institute
    current_user_role = current_user.role_type
    redirect_url_name = STUDENT_CRUD_URL_MAP.get(current_user_role)
    if request.method == "POST":
        form = StudentForm(request.POST, current_user=current_user)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save()
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse(redirect_url_name))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse(redirect_url_name))
    else:
        form = StudentForm(current_user=current_user)
    students = Student.objects.filter(institute=session_institute).order_by("pkid")
    context = {"form": form, "students": students, "state": state}
    if current_user_role == RoleType.OWNER:
        return render(request, "institutes/manage_student/student.html", context)
    else:
        return render(request, "institutes/manage_student/staff_student.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_academic_class_section(request):
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = AcademicClassSectionForm(request.POST)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save(session_institute)
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadAcademicClassSection"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadAcademicClassSection"))
    else:
        form = AcademicClassSectionForm()
    academic_cs = AcademicClassSection.objects.filter(institute=session_institute, is_deleted=False).order_by("pkid")
    context = {"form": form, "academic_cs": academic_cs}
    return render(request, "institutes/manage_academic_cs/academic_class_section.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_academic_session(request):
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = AcademicSessionForm(request.POST)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save(session_institute)
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadAcademicSession"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadAcademicSession"))
    else:
        form = AcademicSessionForm()
    academic_sessions = AcademicSession.objects.filter(institute=session_institute).order_by("pkid")
    context = {"form": form, "academic_sessions": academic_sessions}
    return render(request, "institutes/manage_academic_session/academic_session.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def create_read_academic_info(request):
    # session_institute is the logged in user's institute
    session_institute = request.user.role_data.institute
    if request.method == "POST":
        form = AcademicInfoForm(request.POST, institute=session_institute)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save()
            if status:
                messages.success(request, f"{_message}")
            else:
                messages.warning(request, f"{_message}")
            return redirect(reverse("CreateReadAcademicInfo"))
        else:
            messages.warning(request, f"{form.errors}")
            return redirect(reverse("CreateReadAcademicInfo"))
    else:
        form = AcademicInfoForm(institute=session_institute)
    academic_information = AcademicInfo.objects.filter(institute=session_institute, is_deleted=False).order_by("pkid")
    context = {"form": form, "academic_info": academic_information}
    return render(request, "institutes/manage_academic_info/academic_info.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def delete_academic_info(request):
    if request.method == "POST":
        academic_info_id = request.POST.get("academic_info_id")
        academic_info = AcademicInfo.objects.filter(id=academic_info_id).first()
        if academic_info:
            academic_info.soft_delete()
            messages.success(request, "Academic information deleted successfully.")
        else:
            messages.warning(request, "Academic information not found.")
    return redirect(reverse("CreateReadAcademicInfo"))


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER])
def train_model(request):
    institute = request.user.role_data.institute
    status = start_training(institute)
    if status:
        messages.success(request, "Model trained successfully.")
    else:
        messages.warning(request, "Model training failed.")
    return redirect(reverse("InstituteDashboard"))
