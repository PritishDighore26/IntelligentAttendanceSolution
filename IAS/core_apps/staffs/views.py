from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from IAS.core_apps.attendance.models import Attendance
from IAS.core_apps.common.decorators import allowed_users
from IAS.core_apps.common.models import ROLE_URL_MAP, AttendanceStatus, RoleType
from IAS.core_apps.common.views import get_attendance_data, mark_all_attendance
from IAS.core_apps.students.models import Student


# Create your views here.
@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STAFF])
def dashboard(request):
    current_user = request.user.role_data
    todays_date = date.today()
    student_count = Student.objects.filter(institute=current_user.institute).count()
    attendances, todays_attendance = get_attendance_data(current_user, todays_date)
    student_todays_attendance = Attendance.objects.filter(
        institute=current_user.institute,
        is_deleted=False,
        a_date=todays_date,
        a_type=RoleType.STUDENT,
    )
    present_count = student_todays_attendance.filter(a_status=AttendanceStatus.PRESENT).count()
    absent_count = student_todays_attendance.filter(a_status__in=[AttendanceStatus.ABSENT]).count()
    if request.method == "POST":
        todays_attendance = mark_all_attendance(current_user, todays_attendance)
        messages.success(request, "Attendance updated successfully.")
        todays_attendance = Attendance.objects.get(id=todays_attendance.id)

    context = {
        "attendances": attendances,
        "todays_attendance": todays_attendance,
        "student_count": student_count,
        "present_count": present_count,
        "absent_count": absent_count,
        "student_todays_attendance": student_todays_attendance,
    }
    return render(request, "staffs/dashboard.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STAFF])
def profile(request):
    return render(request, "staffs/manage_profile/profile.html")
