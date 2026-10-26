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
