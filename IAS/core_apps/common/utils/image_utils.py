import logging
import os

import cv2
import dlib
import numpy as np
from django.conf import settings
from imutils.face_utils import FaceAligner
from imutils.face_utils.helpers import FACIAL_LANDMARKS_68_IDXS, shape_to_np

BASE_DIR = settings.BASE_DIR

logger = logging.getLogger(__name__)
# Add path to the shape predictor
SHAPE_PREDICTOR_PATH = os.path.abspath(os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat"))


class CustomFaceAligner(FaceAligner):

    def align(self, image, gray, rect):
        # Convert landmarks to NumPy array
        shape = self.predictor(gray, rect)
        shape = shape_to_np(shape)

        # Extract left and right eye landmarks
        leftEyePts = shape[FACIAL_LANDMARKS_68_IDXS["left_eye"][0]:FACIAL_LANDMARKS_68_IDXS["left_eye"][1]]
        rightEyePts = shape[FACIAL_LANDMARKS_68_IDXS["right_eye"][0]:FACIAL_LANDMARKS_68_IDXS["right_eye"][1]]

        # Compute eye centers
        leftEyeCenter = leftEyePts.mean(axis=0).astype("int")
        rightEyeCenter = rightEyePts.mean(axis=0).astype("int")

        # Compute angle
        dY = rightEyeCenter[1] - leftEyeCenter[1]
        dX = rightEyeCenter[0] - leftEyeCenter[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # Compute scale factor
        dist = np.sqrt((dX**2) + (dY**2))
        desiredDist = (1.0 - self.desiredLeftEye[0] - self.desiredLeftEye[0]) * self.desiredFaceWidth
        scale = desiredDist / dist

        # Fix: Ensure integer values for eyesCenter
        eyesCenter = (int(leftEyeCenter[0] + rightEyeCenter[0]) // 2, int(leftEyeCenter[1] + rightEyeCenter[1]) // 2)

        # Fix: Handle missing values gracefully
        if not (np.isfinite(eyesCenter[0]) and np.isfinite(eyesCenter[1])):
            logger.debug("Invalid eye center values!")
            return None

        # Compute rotation matrix
        M = cv2.getRotationMatrix2D(eyesCenter, angle, scale)
        M[0, 2] += (self.desiredFaceWidth * 0.5 - eyesCenter[0])
        M[1, 2] += (self.desiredFaceHeight * self.desiredLeftEye[1] - eyesCenter[1])

        # Apply transformation
        (w, h) = (self.desiredFaceWidth, self.desiredFaceHeight)
        output = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC)

        return output


def get_detector():
    return dlib.get_frontal_face_detector()


def get_predictor():
    return dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
