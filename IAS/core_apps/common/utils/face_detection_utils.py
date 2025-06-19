import logging

import face_recognition
import numpy as np

logger = logging.getLogger(__name__)


def predict(face_aligned, svc, threshold=0.7):
    try:
        x_face_locations = face_recognition.face_locations(face_aligned)
        faces_encodings = face_recognition.face_encodings(face_aligned, known_face_locations=x_face_locations)
        if len(faces_encodings) == 0:
            return ([-1], [0])

    except Exception as e:
        logger.error(f"Error in face recognition: {e}")
        return ([-1], [0])

    prob = svc.predict_proba(faces_encodings)
    result = np.where(prob[0] == np.amax(prob[0]))
    if prob[0][result[0]] <= threshold:
        return ([-1], prob[0][result[0]])

    return (result[0], prob[0][result[0]])
