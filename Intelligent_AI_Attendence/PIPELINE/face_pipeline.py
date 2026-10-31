import json

import dlib
import face_recognition_models
import numpy as np
import streamlit as st

from src.screens.database.db import get_all_students



FACE_MATCH_THRESHOLD = 0.50


FACE_MATCH_MARGIN = 0.05


MIN_DETECTION_SCORE = 0.25


MIN_FACE_SIZE = 80          
MIN_BRIGHTNESS = 50         
MAX_BRIGHTNESS = 220
MIN_SHARPNESS = 15.0        



# Models and embeddings


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def _prepare_image(image_np):
    """dlib needs an 8-bit RGB image. Accept grayscale, RGBA and other dtypes."""
    image = np.asarray(image_np)

    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)

    if image.ndim == 2:                      
        image = np.stack([image] * 3, axis=-1)
    elif image.ndim == 3 and image.shape[2] == 4:   
        image = image[:, :, :3]

    return np.ascontiguousarray(image)


def _detect_faces(image):
    """Find faces: ignore weak detections, and list the biggest face first."""
    detector, _, _ = load_dlib_models()
    rects, scores, _ = detector.run(image, 1, 0.0)

    faces = [r for r, score in zip(rects, scores) if score >= MIN_DETECTION_SCORE]
    faces.sort(key=lambda r: r.width() * r.height(), reverse=True)
    return faces


def get_face_embeddings(image_np, num_jitters=1):
    """Return one 128-number embedding for every face found in the image.
    The biggest (main) face comes first, so encodings[0] is the person in front.

    num_jitters: how many slightly-changed copies of each face to average.
    Use a higher number (for example 5) when creating a profile: it is slower
    but gives a steadier embedding. Keep 1 for class photos.
    """
    _, sp, facerec = load_dlib_models()
    image = _prepare_image(image_np)
    faces = _detect_faces(image)

    encodings = []

    for face in faces:
        shape = sp(image, face)
        face_descriptor = facerec.compute_face_descriptor(image, shape, num_jitters)

        encodings.append(np.array(face_descriptor))
    return encodings


def check_face_quality(image_np):
    """Check a profile photo. Returns (ok, message).

    Call this before creating a profile so a bad photo (no face, two faces,
    too dark, too small, blurry) is rejected with a clear message instead of
    saving a poor embedding that later causes wrong matches.
    """
    image = _prepare_image(image_np)
    faces = _detect_faces(image)

    if len(faces) == 0:
        return False, "No face found. Look straight at the camera in good light."
    if len(faces) > 1:
        return False, "More than one face found. Only one person should be in the photo."

    face = faces[0]
    height, width = image.shape[:2]
    left, top = max(face.left(), 0), max(face.top(), 0)
    right, bottom = min(face.right(), width), min(face.bottom(), height)

    if min(right - left, bottom - top) < MIN_FACE_SIZE:
        return False, "Your face is too small or too far away. Move closer to the camera."

    crop = image[top:bottom, left:right].astype(float).mean(axis=2)

    brightness = crop.mean()
    if brightness < MIN_BRIGHTNESS:
        return False, "The photo is too dark. Face a light and try again."
    if brightness > MAX_BRIGHTNESS:
        return False, "The photo is too bright. Avoid strong light behind or on your face."

    # Sharpness: how much the pixel values change from point to point.
    laplacian = (
        -4 * crop[1:-1, 1:-1]
        + crop[:-2, 1:-1] + crop[2:, 1:-1]
        + crop[1:-1, :-2] + crop[1:-1, 2:]
    )
    if laplacian.var() < MIN_SHARPNESS:
        return False, "The photo is blurry. Hold still and try again."

    return True, "OK"



# Stored faces


def _to_vector(embedding):
    """Turn a stored embedding (list, or JSON text) into a 128-number array, or None."""
    if embedding is None:
        return None
    try:
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        vec = np.asarray(embedding, dtype=float)
    except Exception:
        return None
    return vec if vec.shape == (128,) else None


@st.cache_resource
def get_trained_model():
    """Load every student's stored face once. (Name kept so other files still work.)"""
    student_db = get_all_students()

    if not student_db:
        return None

    X = []
    y = []

    for student in student_db:
        vec = _to_vector(student.get('face_embedding'))
        if vec is not None:
            X.append(vec)
            y.append(student.get('student_id'))

    if len(X) == 0:
        return 0

    return {'X': np.vstack(X), 'y': y}


def train_classifier():
    """Call this after a new student is saved so the new face is included."""
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)



# Matching


def _nearest(encoding, X_train, y_train):
    """Return (student_id, distance) of the closest stored face."""
    distances = np.linalg.norm(X_train - encoding, axis=1)
    best = int(np.argmin(distances))
    return y_train[best], float(distances[best]), distances


def _identify(encoding, X_train, y_train):
    """Return the student_id this face belongs to, or None if it is not a clear match."""
    best_id, best_distance, distances = _nearest(encoding, X_train, y_train)

   
    if best_distance > FACE_MATCH_THRESHOLD:
        return None

    
    rivals = [d for d, sid in zip(distances, y_train) if sid != best_id]
    if rivals and (min(rivals) - best_distance) < FACE_MATCH_MARGIN:
        return None

    return best_id


def find_existing_student_id(embedding):
    """Return the student_id whose stored face matches this one, or None.

    Use this when creating a profile, to stop the same person registering twice.
    """
    model_data = get_trained_model()
    if not model_data:
        return None

    best_id, best_distance, _ = _nearest(
        np.asarray(embedding, dtype=float), model_data['X'], model_data['y']
    )
    return best_id if best_distance <= FACE_MATCH_THRESHOLD else None


def predict_attendance(class_image_np):
    """Return (students found, all enrolled student ids, number of faces in the photo)."""
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(set(y_train))

    for encoding in encodings:
        student_id = _identify(encoding, X_train, y_train)
        if student_id is not None:
            detected_student[int(student_id)] = True

    return detected_student, all_students, len(encodings)