import io
import json

import librosa
import numpy as np
import streamlit as st
from resemblyzer import VoiceEncoder, preprocess_wav

try:
    import webrtcvad  # installed together with resemblyzer
except Exception:
    webrtcvad = None


SAMPLE_RATE = 16000

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Matching. Similarity runs from 0 (different voice) to 1 (identical voice).
VOICE_MATCH_THRESHOLD = 0.60   # best match must be at least this similar
VOICE_MATCH_MARGIN = 0.02      # ...and beat the runner-up by this much (0 = off)

# Cutting the recording into one piece per speaker.
MIN_PAUSE_SECONDS = 0.7        # a silence this long starts a new speaker
MIN_SEGMENT_SECONDS = 0.6      # ignore anything shorter
MAX_SEGMENT_SECONDS = 3.0      # speech longer than this is checked in windows
WINDOW_SECONDS = 3.0
WINDOW_HOP_SECONDS = 1.5
VAD_AGGRESSIVENESS = 2         # 0-3, higher = stricter about what counts as speech

# Voice sample taken when a student creates a profile.
MIN_ENROLL_SECONDS = 3.0


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_vector(embedding):
    """Turn a stored voice embedding (list or JSON text) into a unit vector, or None."""
    if embedding is None:
        return None
    try:
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        vec = np.asarray(embedding, dtype=float)
    except Exception:
        return None
    if vec.ndim != 1 or vec.size == 0:
        return None
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else None


def _speech_flags(audio, frame_ms=30):
    """True for every 30 ms frame that contains speech. Returns (flags, frame_samples)."""
    frame_len = int(SAMPLE_RATE * frame_ms / 1000)
    n_frames = len(audio) // frame_len
    if n_frames == 0:
        return np.zeros(0, dtype=bool), frame_len

    if webrtcvad is not None:
        vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
        flags = np.zeros(n_frames, dtype=bool)
        for i in range(n_frames):
            frame = pcm[i * frame_len:(i + 1) * frame_len].tobytes()
            flags[i] = vad.is_speech(frame, SAMPLE_RATE)
        return flags, frame_len

    # Fallback if webrtcvad is missing: speech = clearly louder than background noise.
    rms = librosa.feature.rms(
        y=audio, frame_length=frame_len, hop_length=frame_len
    )[0][:n_frames]
    noise_floor = np.percentile(rms, 20)
    return rms > (noise_floor * 3 + 1e-4), frame_len


def _group_speech(flags, frame_seconds, min_pause=MIN_PAUSE_SECONDS):
    """Join speech frames into pieces; a pause >= min_pause starts a new piece.

    Returns a list of (first_frame, last_frame).
    """
    speech = np.flatnonzero(flags)
    if speech.size == 0:
        return []

    pieces = []
    start = prev = int(speech[0])
    for i in speech[1:]:
        i = int(i)
        if (i - prev - 1) * frame_seconds >= min_pause:
            pieces.append((start, prev))
            start = i
        prev = i
    pieces.append((start, prev))
    return pieces


def _windows(start, end):
    """Long speech may contain several people with no pause between them,
    so check it in overlapping windows."""
    max_len = int(MAX_SEGMENT_SECONDS * SAMPLE_RATE)
    if end - start <= max_len:
        return [(start, end)]

    win = int(WINDOW_SECONDS * SAMPLE_RATE)
    hop = int(WINDOW_HOP_SECONDS * SAMPLE_RATE)
    out = []
    s = start
    while s + win < end:
        out.append((s, s + win))
        s += hop
    out.append((max(start, end - win), end))
    return out


def _speech_segments(audio):
    """Return (start_sample, end_sample) for each stretch of speech."""
    flags, frame_len = _speech_flags(audio)
    pieces = _group_speech(flags, frame_len / SAMPLE_RATE)

    pad = int(0.15 * SAMPLE_RATE)
    segments = []
    for first, last in pieces:
        start = max(first * frame_len - pad, 0)
        end = min((last + 1) * frame_len + pad, len(audio))
        segments.append((start, end))
    return segments


def _score_all(new_embedding, candidates_dict):
    """Similarity of one embedding against every candidate: {student_id: score}."""
    probe = _to_vector(new_embedding)
    if probe is None or not candidates_dict:
        return {}

    scores = {}
    for sid, stored in candidates_dict.items():
        vec = _to_vector(stored)
        if vec is not None and vec.shape == probe.shape:
            scores[sid] = float(np.dot(probe, vec))
    return scores


def _decide(scores, threshold, margin):
    """Pick a clear winner from {student_id: score}, or (None, best_score)."""
    if not scores:
        return None, 0.0

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_sid, best_score = ranked[0]

    if best_score < threshold:
        return None, best_score

    # Another student sounds almost as similar -> too risky to guess.
    if margin > 0 and len(ranked) > 1 and (best_score - ranked[1][1]) < margin:
        return None, best_score

    return best_sid, best_score


# ---------------------------------------------------------------------------
# Profile voice sample
# ---------------------------------------------------------------------------

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=SAMPLE_RATE, mono=True)
        wav = preprocess_wav(audio)

        if len(wav) < MIN_ENROLL_SECONDS * SAMPLE_RATE:
            st.warning(
                "Your voice sample is too short. Record at least 3 seconds of "
                "clear speech, for example: 'I am present, my name is ...'. "
                "Voice attendance will not work for you until you do."
            )
            return None

        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Voice recognition error: {e}")
        return None


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def identify_speaker(new_embedding, candidates_dict,
                     threshold=VOICE_MATCH_THRESHOLD, margin=VOICE_MATCH_MARGIN):
    """Return (student_id, similarity), or (None, best_similarity) if no clear match."""
    scores = _score_all(new_embedding, candidates_dict)
    return _decide(scores, threshold, margin)


def process_bulk_audio(audio_bytes, candidates_dict,
                       threshold=VOICE_MATCH_THRESHOLD, margin=VOICE_MATCH_MARGIN,
                       return_debug=False):
    """Find every enrolled student who speaks in one recording.

    Returns {student_id: similarity} for detected students.
    With return_debug=True returns (detected, best_raw), where best_raw holds the
    highest similarity every student reached, even if they were not accepted.
    """
    empty = ({}, {}) if return_debug else {}
    try:
        encoder = load_voice_encoder()

        audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=SAMPLE_RATE, mono=True)
        if len(audio) == 0:
            return empty

        identified = {}
        best_raw = {}

        for seg_start, seg_end in _speech_segments(audio):
            for start, end in _windows(seg_start, seg_end):
                wav = preprocess_wav(audio[start:end])

                if len(wav) < MIN_SEGMENT_SECONDS * SAMPLE_RATE:
                    continue

                embedding = encoder.embed_utterance(wav)
                scores = _score_all(embedding, candidates_dict)

                for sid, score in scores.items():
                    if score > best_raw.get(sid, -1.0):
                        best_raw[sid] = score

                sid, score = _decide(scores, threshold, margin)
                if sid is not None and score > identified.get(sid, -1.0):
                    identified[sid] = score

        return (identified, best_raw) if return_debug else identified

    except Exception as e:
        st.error(f"Voice attendance error: {e}")
        return empty