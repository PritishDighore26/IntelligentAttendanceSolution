from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from IAS.core_apps.attendance.models import Attendance
from IAS.core_apps.common.decorators import allowed_users
from IAS.core_apps.common.models import ROLE_URL_MAP, AttendanceStatus, RoleType
from IAS.core_apps.common.views import get_attendance_data, mark_all_attendance


def get_months_map():
    """
    Returns a dictionary mapping month digits to abbreviated month names.
    """
    import calendar

    return {i: calendar.month_abbr[i] for i in range(1, 13)}


# Create your views here.
@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STUDENT])
def dashboard(request):
    current_user = request.user.role_data
    todays_date = date.today()
    attendances, todays_attendance = get_attendance_data(current_user, todays_date)
    months_map = get_months_map()
    filter_status = request.GET.get("status")
    filter_month = request.GET.get("month", date.today().strftime("%m"))  # Get the month from query params
    if filter_month and filter_month.isdigit():  # Validate that the month is a number
        filter_month = int(filter_month)
    present_count = (
        attendances.filter(a_date__month=filter_month, a_status=AttendanceStatus.PRESENT).count() if attendances else 0
    )
    absent_count = (
        attendances.filter(a_date__month=filter_month, a_status=AttendanceStatus.ABSENT).count() if attendances else 0
    )
    leave_count = (
        attendances.filter(a_date__month=filter_month, a_status=AttendanceStatus.ON_LEAVE).count() if attendances else 0
    )

    if request.method == "POST":
        todays_attendance = mark_all_attendance(current_user, todays_attendance)
        messages.success(request, "Attendance updated successfully.")
        todays_attendance = Attendance.objects.get(id=todays_attendance.id)

    context = {
        "attendances": (attendances.filter(a_status=filter_status) if filter_status else attendances),
        "todays_attendance": todays_attendance,
        "months_map": months_map,
        "present_count": present_count,
        "absent_count": absent_count,
        "leave_count": leave_count,
        "current_month": months_map[filter_month],
        "attendance_status": AttendanceStatus,
    }
    return render(request, "students/dashboard.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STUDENT, RoleType.OWNER, RoleType.STAFF])
def attendance_create_read(request):
    current_user = request.user.role_data
    attendances, todays_attendance = get_attendance_data(current_user, filter_date=date.today())
    context = {"attendances": attendances, "todays_attendance": todays_attendance}
    return render(request, "attendance/manage_attendance/attendance.html", context)
