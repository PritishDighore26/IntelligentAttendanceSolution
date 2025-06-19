import base64
import json
import logging
import os
import pickle
import tempfile
import time
from datetime import date

import cv2
import imutils
import numpy as np
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from imutils import face_utils
from sklearn.preprocessing import LabelEncoder

from IAS.core_apps.attendance.filters import AttendanceFilter
from IAS.core_apps.attendance.models import Attendance
from IAS.core_apps.attendance.resources import AttendanceResource
from IAS.core_apps.common.decorators import allowed_users
from IAS.core_apps.common.models import ROLE_URL_MAP, AttendanceStatus, BloodGroup, Gender, RoleType
from IAS.core_apps.common.utils.datetime_utils import get_current_time
from IAS.core_apps.common.utils.face_detection_utils import predict
from IAS.core_apps.common.utils.image_utils import CustomFaceAligner as FaceAligner
from IAS.core_apps.common.utils.image_utils import get_detector, get_predictor
from IAS.core_apps.institutes.models import Institute
from IAS.core_apps.staffs.models import Staff
from IAS.core_apps.students.models import AcademicInfo, Student
from IAS.core_apps.users.models import Role
from IAS.ias.general import BASE_DIR

logger = logging.getLogger(__name__)

User = get_user_model()


def camera(request):
    return render(request, "common/camera.html")


def register_face(request):
    return render(request, "common/register_face.html")


@csrf_exempt
def mark_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=400)

    if "image" not in request.FILES:
        return JsonResponse({"error": "No image provided"}, status=400)

    # Initialize face recognition components
    detector = get_detector()
    predictor = get_predictor()
    svc_save_path = os.path.join(BASE_DIR, "face_recognition_data/svc.sav")

    with open(svc_save_path, "rb") as f:
        svc = pickle.load(f)
    fa = FaceAligner(predictor, desiredFaceWidth=100)
    encoder = LabelEncoder()
    clss_path = os.path.join(BASE_DIR, "face_recognition_data/classes.npy")
    encoder.classes_ = np.load(clss_path)

    # Initialize counters
    faces_encodings = np.zeros((1, 128))
    no_of_faces = len(svc.predict_proba(faces_encodings)[0])
    count = dict()
    present = dict()
    start = dict()

    for i in range(no_of_faces):
        user_id = encoder.inverse_transform([i])[0]
        count[user_id] = 0
        present[user_id] = False

    # Process the uploaded image
    image_file = request.FILES["image"]
    image_array = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    frame = imutils.resize(frame, width=800)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame, 0)

    for face in faces:
        (x, y, w, h) = face_utils.rect_to_bb(face)
        face_aligned = fa.align(frame, gray_frame, face)
        (pred, prob) = predict(face_aligned, svc)

        if pred != [-1]:
            user_id = encoder.inverse_transform(np.ravel([pred]))[0]
            if count[user_id] == 0:
                start[user_id] = time.time()
                count[user_id] += 1

            if count[user_id] == 4 and (time.time() - start[user_id]) > 1.2:
                count[user_id] = 0
            else:
                present[user_id] = True
                count[user_id] += 1
                logger.info(f"Found user: {user_id}, Present: {present[user_id]}, Count: {count[user_id]}")

    name = update_attendance_in_db_in(present)
    return JsonResponse({"name": name})


def get_user_ids_with_true_values(input_dict):
    return [key for key, value in input_dict.items() if value]


def get_attendance_data(current_user, filter_date):
    session_institute = current_user.institute
    attendances = []
    todays_attendance = Attendance.objects.none()
    if current_user.role_type == RoleType.STUDENT:
        student = Student.objects.get(role=current_user, institute=session_institute)
        academic_info = AcademicInfo.objects.filter(student=student).order_by("pkid")
        if academic_info:
            academic_info = academic_info[0]
            attendances = Attendance.objects.filter(academic_info=academic_info,
                                                    a_date__lt=filter_date).order_by("-a_date")
            todays_attendance, _ = Attendance.objects.get_or_create(
                a_date=filter_date,
                institute=session_institute,
                academic_info=academic_info,
                academic_class_section=academic_info.academic_class_section,
                session=academic_info.session,
                a_type=RoleType.STUDENT,
            )
    elif current_user.role_type == RoleType.STAFF:
        staff = Staff.objects.get(role=current_user, institute=session_institute)
        attendances = Attendance.objects.filter(staff=staff, a_date__lt=filter_date).order_by("-a_date")
        todays_attendance, _ = Attendance.objects.get_or_create(
            a_date=filter_date,
            institute=session_institute,
            staff=staff,
            a_type=RoleType.STAFF,
        )
    return attendances, todays_attendance


def update_attendance_in_db_in(clock_in_data):
    user_ids = get_user_ids_with_true_values(clock_in_data)
    name = ""
    for user_id in user_ids:
        # Mark attendance for user_id
        user = User.objects.get(id=user_id)
        current_user = Role.objects.get(user=user)
        name = current_user.user.full_name
        logger.info(f"Marking Attendance for User {current_user.user.full_name}")
        _, todays_attendance = get_attendance_data(current_user, date.today())
        todays_attendance = mark_all_attendance(current_user, todays_attendance)
    return name


def mark_all_attendance(current_user, todays_attendance):
    with transaction.atomic():
        created_by_uuid_role = f"{current_user.user.id}/{current_user.role_type}"
        current_time = get_current_time()
        if not todays_attendance.a_in_time:
            todays_attendance.a_in_time = current_time
            todays_attendance.a_status = AttendanceStatus.PRESENT
            todays_attendance.created_by_uuid_role = created_by_uuid_role
            todays_attendance.a_type = current_user.role_type
        else:
            todays_attendance.a_out_time = current_time
            todays_attendance.a_type = current_user.role_type
            todays_attendance.a_status = AttendanceStatus.PRESENT
        todays_attendance.save()
    return todays_attendance


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STUDENT, RoleType.STAFF])
def add_images_to_dataset(request):
    try:
        if request.method == "POST" and request.FILES.get("image"):
            user = request.user.role_data.user
            user_id = user.id
            institute_id = request.user.role_data.institute.id
            directory = os.path.join(BASE_DIR, f"image_dataset//{institute_id}//{user_id}")
            logger.info(f"Directory: {directory}")
            # Ensure the directory exists
            os.makedirs(directory, exist_ok=True)

            image_file = request.FILES["image"]
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            image_array = np.asarray(bytearray(open(tmp_path, "rb").read()), dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            frame = imutils.resize(frame, width=800)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detector = get_detector()
            faces = detector(gray_frame, 0)
            predictor = get_predictor()
            fa = FaceAligner(predictor, desiredFaceWidth=100)
            start_sample_num = user.last_image_number

            logger.info(f"faces detected: {len(faces)}")

            for face in faces:
                # fa.align is being used to align the face
                face_aligned = fa.align(frame, gray_frame, face)
                current_image = os.path.join(directory, f"{start_sample_num}.jpg")
                cv2.imwrite(current_image, face_aligned)
                logger.info(f"Image saved: {current_image}")

            user.last_image_number += 1
            user.save()

        return JsonResponse({"success": "Done"})
    except Exception as e:
        logger.error(f"Error in add_images_to_dataset: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.STUDENT, RoleType.OWNER, RoleType.STAFF])
def profile(request):
    current_user = request.user.role_data
    if current_user.role_type == RoleType.STUDENT:
        student = Student.objects.get(role=current_user)
        if request.method == "POST":
            dob = request.POST.get("dob")
            state = request.POST.get("state", "")
            about = request.POST.get("about", "")
            gender = request.POST.get("gender", "")
            address = request.POST.get("address", "")
            blood_group = request.POST.get("blood_group", "")
            profile_image = request.FILES.get("profile_image", "")
            mobile_no = request.POST.get("mobile_no", "")

            student.dob = dob
            student.state = state
            student.about = about
            student.gender = gender
            student.address = address
            student.blood_group = blood_group
            student.profile_image = profile_image
            student.mobile_no = mobile_no
            student.save()

            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("ProfileUpdateRead"))
    elif current_user.role_type == RoleType.OWNER:
        institute = Institute.objects.get(id=current_user.institute.id)
        if request.method == "POST":
            institute_name = request.POST.get("institute_name", "")
            institute_reg_number = request.POST.get("institute_reg_number", "")
            phone_number = request.POST.get("phone_number", "")
            address = request.POST.get("address", "")
            city = request.POST.get("city", "")
            institute_image = request.FILES.get("institute_image", None)

            institute.institute_name = institute_name
            institute.institute_reg_number = institute_reg_number
            institute.phone_number = phone_number
            institute.address = address
            institute.city = city
            if institute_image:
                institute.institute_image = institute_image
            institute.save()

            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("ProfileUpdateRead"))
    elif current_user.role_type == RoleType.STAFF:
        staff = Staff.objects.get(role=current_user)
        if request.method == "POST":
            profile_image = request.FILES.get("profile_image", None)
            dob = request.POST.get("dob", "")
            state = request.POST.get("state", "")
            address = request.POST.get("address", "")
            gender = request.POST.get("gender", "")
            blood_group = request.POST.get("blood_group", "")
            mobile_no = request.POST.get("mobile_no", "")
            about = request.POST.get("about", "")
            if profile_image:
                staff.profile_image = profile_image
            staff.dob = dob
            staff.state = state
            staff.address = address
            staff.blood_group = blood_group
            staff.gender = gender
            staff.mobile_no = mobile_no
            staff.about = about
            staff.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("ProfileUpdateRead"))

    context = {"blood_groups": BloodGroup, "genders": Gender}
    return render(request, "common/manage_profile/profile.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER, RoleType.STAFF])
def attendance_list(request):
    # session_institute is the logged in user's institute
    current_user = request.user.role_data
    session_institute = request.user.role_data.institute
    if current_user.role_type == RoleType.STAFF:
        attendance_queryset = Attendance.objects.filter(
            institute=session_institute, is_deleted=False, a_type=RoleType.STUDENT
        )
    else:
        attendance_queryset = Attendance.objects.filter(institute=session_institute, is_deleted=False)
    attendance_filter = AttendanceFilter(request.GET, queryset=attendance_queryset)

    context = {
        "todays_attendance": attendance_filter.qs,
        "attendance_filter": attendance_filter,
    }
    return render(request, "attendance/manage_attendance/attendance.html", context)


@login_required(login_url=ROLE_URL_MAP[RoleType.ANONYMOUS])
@allowed_users(allowed_roles=[RoleType.OWNER, RoleType.STAFF])
def export_attendance_csv(request):
    current_user = request.user.role_data
    session_institute = request.user.role_data.institute
    if current_user.role_type == RoleType.STAFF:
        attendance_queryset = Attendance.objects.filter(
            institute=session_institute, is_deleted=False, a_type=RoleType.STUDENT
        )
    else:
        attendance_queryset = Attendance.objects.filter(institute=session_institute, is_deleted=False)
    attendance_filter = AttendanceFilter(request.GET, queryset=attendance_queryset)
    dataset = AttendanceResource().export(attendance_filter.qs)

    response = HttpResponse(dataset.csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="filtered_attendance.csv"'
    return response


@csrf_exempt
def process_frame(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=400)

    try:
        data = json.loads(request.body)
        frame_data = data.get("frame")
        if not frame_data:
            return JsonResponse({"error": "No frame data provided"}, status=400)

        # Remove the data URL prefix to get the base64 data
        frame_data = frame_data.split(",")[1]

        # Convert base64 to image
        image_bytes = base64.b64decode(frame_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Initialize face recognition components
        detector = get_detector()
        predictor = get_predictor()
        svc_save_path = os.path.join(BASE_DIR, "face_recognition_data/svc.sav")

        with open(svc_save_path, "rb") as f:
            svc = pickle.load(f)
        fa = FaceAligner(predictor, desiredFaceWidth=100)
        encoder = LabelEncoder()
        class_path = os.path.join(BASE_DIR, "face_recognition_data/classes.npy")
        encoder.classes_ = np.load(class_path)

        # Process frame
        frame = imutils.resize(frame, width=800)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray_frame, 0)

        detected_faces = []
        for face in faces:
            (x, y, w, h) = face_utils.rect_to_bb(face)
            face_aligned = fa.align(frame, gray_frame, face)
            (pred, prob) = predict(face_aligned, svc)

            if pred != [-1]:
                user_id = encoder.inverse_transform(np.ravel([pred]))[0]
                user = User.objects.get(id=user_id)
                detected_faces.append({
                    "user_id": user_id,
                    "name": user.full_name,
                    "confidence": float(prob[0]),
                    "bbox": [x, y, w, h],
                })

        return JsonResponse({"success": True, "faces": detected_faces})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
