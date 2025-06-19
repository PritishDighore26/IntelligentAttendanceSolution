import logging
import os
import pickle

import cv2
import django
import face_recognition
import numpy as np
from face_recognition.face_recognition_cli import image_files_in_folder
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

from IAS.ias.general import BASE_DIR

# Set up Django settings if not will 'raise AppRegistryNotReady("Apps aren't loaded yet.")'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IAS.ias.settings")
django.setup()

logger = logging.getLogger(__name__)


def delete_trained_images(training_dir: str) -> None:
    """Delete all images in the training directory."""
    for user_id in os.listdir(training_dir):
        curr_directory = os.path.join(training_dir, user_id)
        if not os.path.isdir(curr_directory):
            continue
        for imagefile in image_files_in_folder(curr_directory):
            os.remove(imagefile)
        os.rmdir(curr_directory)
        logging.info(f"Deleted images for user {user_id} in {curr_directory}.")


def start_training(institute) -> bool:
    try:
        logger.info(f"Training Started for {institute.institute_name}.")
        training_dir = os.path.join(BASE_DIR, f"image_dataset/{institute.id}")
        if not os.path.exists(training_dir):
            logger.info(f"Training Directory not found for {institute.institute_name}")
            logger.info("Please upload images from any Student, Staff and Institute Login.\n")
            return False

        X = []
        y = []
        i = 0
        for user_id in os.listdir(training_dir):
            curr_directory = os.path.join(training_dir, user_id)
            if not os.path.isdir(curr_directory):
                continue
            for imagefile in image_files_in_folder(curr_directory):
                image = cv2.imread(imagefile)
                try:
                    X.append((face_recognition.face_encodings(image)[0]).tolist())

                    y.append(user_id)
                    i += 1
                except Exception as e:
                    logger.error(f"Error in image {imagefile}: {e}")
                    os.remove(imagefile)
                    logger.info(f"removed imagefile {imagefile}")

        encoder = LabelEncoder()
        encoder.fit(y)
        y = encoder.transform(y)
        X1 = np.array(X)

        trained_data_path = os.path.join(BASE_DIR, "face_recognition_data")
        if not os.path.exists(trained_data_path):
            os.mkdir(trained_data_path)
        classes_path = os.path.join(trained_data_path, "classes.npy")
        np.save(classes_path, encoder.classes_)
        svc = SVC(kernel="linear", probability=True)
        svc.fit(X1, y)

        svc_save_path = os.path.join(trained_data_path, "svc.sav")
        with open(svc_save_path, "wb") as f:
            pickle.dump(svc, f)
        logger.info(f"Training Completed for {institute.institute_name}.")
        return True
    except Exception as e:
        logger.error(f"Training Failed for {institute.institute_name}: {e}")
        return False


if __name__ == "__main__":
    from IAS.core_apps.institutes.models import Institute

    institutes = Institute.objects.filter(is_deleted=False)
    for institute in institutes:
        result = start_training(institute)
        if result:
            logger.info(f"Training Completed for {institute.institute_name}.")
        else:
            logger.info(f"Training Failed for {institute.institute_name}.")
