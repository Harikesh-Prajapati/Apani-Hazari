# import numpy as np
# import streamlit as st
# import dlib
# import face_recognition_models

# from sklearn.svm import SVC
# from src.screens.database.db import get_all_students


# @st.cache_resource
# def load_dlib_models():
#     detector = dlib.get_frontal_face_detector() 


#     sp = dlib.shape_predictor(
#         face_recognition_models.pose_predictor_model_location()
#     )

#     facerec = dlib.face_recognition_model_v1(
#         face_recognition_models.face_recognition_model_location()
#     )

#     return detector, sp, facerec

# def get_face_embeddings(image_np):
#     detector, sp, facerec = load_dlib_models()
#     faces = detector(image_np, 1)

#     encodings= []

#     for face in faces:
#         shape = sp(image_np, face)
#         face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) #128 embedding

#         encodings.append(np.array(face_descriptor))
#     return encodings

# @st.cache_resource
# def get_trained_model():
#     X = []
#     y = []


#     student_db = get_all_students()

#     if not student_db:
#         return None
    
#     for student in student_db:
#         embedding = student.get('face_embedding')
#         if embedding:
#             X.append(np.array(embedding))
#             y.append(student.get('student_id'))

#     if len(X) ==0:
#         return 0
    
#     clf = SVC(kernel='linear', probability=True, class_weight='balanced')

#     try:
#         clf.fit(X, y)
#     except ValueError:
#         pass

#     return {'clf': clf, 'X':X, "y":y}


# def train_classifier():
#     st.cache_resource.clear()
#     model_data = get_trained_model()
#     return bool(model_data)

# def predict_attendance(class_image_np):
#     encodings = get_face_embeddings(class_image_np)

#     detected_student = {}


#     model_data = get_trained_model()

#     if not model_data:
#         return detected_student, [], len(encodings)
    
#     clf = model_data['clf']
#     X_train = model_data['X']
#     y_train = model_data['y']

#     all_students = sorted(list(set(y_train)))

#     for encoding in encodings:
#         if len(all_students)>= 2:
#             predicted_id= int(clf.predict([encoding])[0])
#         else:
#             predicted_id = int(all_students[0])

#         student_embedding = X_train[y_train.index(predicted_id)]

#         best_match_score = np.linalg.norm(student_embedding - encoding)

#         resemblance_threshold = 0.6

#         if best_match_score <= resemblance_threshold:
#             detected_student[predicted_id] = True
#     return detected_student, all_students, len(encodings)





"""
Minimal drop-in replacement for the `face_recognition` package.

Why: `face-recognition` depends on `dlib`, which has to be compiled from source
(about 45 minutes, and it fails on Streamlit Community Cloud). This module offers
the same functions on top of the prebuilt `dlib-bin` wheel, so nothing is compiled.

Based on the MIT-licensed face_recognition library by Adam Geitgey.
"""
import warnings

import numpy as np
from PIL import Image

import dlib

with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # face_recognition_models uses pkg_resources
    import face_recognition_models

_face_detector = dlib.get_frontal_face_detector()
_pose_predictor_68 = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
_pose_predictor_5 = dlib.shape_predictor(face_recognition_models.pose_predictor_five_point_model_location())
_face_encoder = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
_cnn_face_detector = None  # loaded only if model="cnn" is requested


def load_image_file(file, mode="RGB"):
    im = Image.open(file)
    if mode:
        im = im.convert(mode)
    return np.array(im)


def _rect_to_css(rect):
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def _css_to_rect(css):
    return dlib.rectangle(css[3], css[0], css[1], css[2])


def _trim_css_to_bounds(css, image_shape):
    return (
        max(css[0], 0),
        min(css[1], image_shape[1]),
        min(css[2], image_shape[0]),
        max(css[3], 0),
    )


def _raw_face_locations(img, number_of_times_to_upsample=1, model="hog"):
    global _cnn_face_detector
    if model == "cnn":
        if _cnn_face_detector is None:
            _cnn_face_detector = dlib.cnn_face_detection_model_v1(
                face_recognition_models.cnn_face_detector_model_location()
            )
        return _cnn_face_detector(img, number_of_times_to_upsample)
    return _face_detector(img, number_of_times_to_upsample)


def face_locations(img, number_of_times_to_upsample=1, model="hog"):
    if model == "cnn":
        return [
            _trim_css_to_bounds(_rect_to_css(face.rect), img.shape)
            for face in _raw_face_locations(img, number_of_times_to_upsample, "cnn")
        ]
    return [
        _trim_css_to_bounds(_rect_to_css(face), img.shape)
        for face in _raw_face_locations(img, number_of_times_to_upsample, model)
    ]


def _raw_face_landmarks(face_image, face_locations=None, model="large"):
    if face_locations is None:
        face_locations = _raw_face_locations(face_image)
    else:
        face_locations = [_css_to_rect(face_location) for face_location in face_locations]

    pose_predictor = _pose_predictor_5 if model == "small" else _pose_predictor_68
    return [pose_predictor(face_image, face_location) for face_location in face_locations]


def face_encodings(face_image, known_face_locations=None, num_jitters=1, model="small"):
    raw_landmarks = _raw_face_landmarks(face_image, known_face_locations, model)
    return [
        np.array(_face_encoder.compute_face_descriptor(face_image, landmark_set, num_jitters))
        for landmark_set in raw_landmarks
    ]


def face_distance(face_encodings, face_to_compare):
    if len(face_encodings) == 0:
        return np.empty((0))
    return np.linalg.norm(face_encodings - face_to_compare, axis=1)


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)



















