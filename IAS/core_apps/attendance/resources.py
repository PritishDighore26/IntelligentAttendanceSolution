from import_export import fields, resources

from IAS.core_apps.common.models import RoleType

from .models import Attendance


# Define a resource for export
class AttendanceResource(resources.ModelResource):
    # Define custom fields to include properties
    a_type = fields.Field(column_name="Type", attribute="a_type")
    a_date = fields.Field(column_name="Date", attribute="a_date")
    in_time = fields.Field(column_name="In Time", attribute="in_time")
    out_time = fields.Field(column_name="Out Time", attribute="out_time")
    a_status = fields.Field(column_name="Status", attribute="a_status")
    # created_by_name = fields.Field(column_name="Marked By", attribute="created_by_name")

    # Custom fields for Student/Staff Info
    user_name = fields.Field(column_name="Name", attribute="user_name")
    user_email = fields.Field(column_name="Email", attribute="user_email")
    user_identifier = fields.Field(column_name="Enrollment No. / Employee Id", attribute="user_identifier")
    class_identifier = fields.Field(column_name="Class - Section", attribute="class_identifier")

    class Meta:
        model = Attendance
        fields = (
            "a_type",
            "a_date",
            "in_time",
            "out_time",
            "a_status",
            "user_name",
            "user_email",
            "user_identifier",
            "class_identifier",  # "created_by_name"
        )

    def dehydrate_user_name(self, obj):
        """Retrieve Name based on Student or Staff"""
        if (obj.a_type == RoleType.STUDENT and obj.academic_info and obj.academic_info.student):
            return obj.academic_info.student.role.user.full_name
        elif obj.a_type == RoleType.STAFF and obj.staff:
            return obj.staff.role.user.full_name
        return "Unknown"

    def dehydrate_user_email(self, obj):
        """Retrieve Email based on Student or Staff"""
        if (obj.a_type == RoleType.STUDENT and obj.academic_info and obj.academic_info.student):
            return obj.academic_info.student.role.user.email
        elif obj.a_type == RoleType.STAFF and obj.staff:
            return obj.staff.role.user.email
        return "N/A"

    def dehydrate_user_identifier(self, obj):
        """Retrieve Enrollment Number for Students, PKID for Staff"""
        if (obj.a_type == RoleType.STUDENT and obj.academic_info and obj.academic_info.student):
            return obj.academic_info.student.enrollment_number
        elif obj.a_type == RoleType.STAFF and obj.staff:
            return obj.staff.id
        return "N/A"

    def dehydrate_class_identifier(self, obj):
        """Retrieve Class Secttion for Students"""
        if (obj.a_type == RoleType.STUDENT and obj.academic_info and obj.academic_info.student):
            return (
                f"{obj.academic_info.academic_class_section.class_name} - "
                f"{obj.academic_info.academic_class_section.class_name}"
            )
        return "N/A"
