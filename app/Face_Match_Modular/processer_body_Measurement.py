import os
import time
import logging
import numpy as np
import cv2
import face_recognition
import mediapipe as mp

from datetime import datetime
from config import (
    temp_frames,
    matched_dir,
    threshold,
    model_type,
    resize_width,
    time_window,
    brightness_threshold
)
from image_utils import is_blurry, sharpen, adjust_brightness, extract_timestamp
from suspect_utils import reload_if_needed
from db_utils import log_to_db
from csv_utils import log_to_csv

# Initialize MediaPipe Pose for body measurements
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Suppress OpenCV file I/O warnings
try:
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception:
    try:
        cv2.setLogLevel(3)
    except Exception:
        pass

logger = logging.getLogger(__name__)

def safe_remove(path: str):
    """Safely remove a file, ignoring if it doesn't exist."""
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug(f"No file to remove: {path}")

def match_body_measurements(detected_measurements, suspects):
    """Compares detected body measurements with stored suspect data."""
    min_distance = float("inf")
    best_match = None

    for suspect_name, suspect_measures in suspects.items():
        distance = np.sqrt(sum((detected_measurements[key] - suspect_measures[key])**2 for key in suspect_measures))
        if distance < min_distance:
            min_distance = distance
            best_match = suspect_name

    return best_match if min_distance < threshold else None

def extract_body_measurements(image):
    """Uses MediaPipe Pose to extract key body measurements."""
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        return {
            "shoulder_width": abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x - landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x),
            "torso_height": abs(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y - landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y),
            "leg_length": abs(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y - landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y)
        }
    return None

def process_frame(frame_fn: str):
    """Process a single frame including body and face recognition."""
    src = os.path.join(temp_frames, frame_fn)
    logger.info(f"Processing frame: {frame_fn}")

    try:
        suspects = reload_if_needed()
        ts = extract_timestamp(frame_fn)

        # Drop too-old frames
        if ts < datetime.now() - time_window:
            logger.warning(f"Frame too old ({ts}), deleting")
            safe_remove(src)
            return

        # Wait for file to be fully written
        for _ in range(5):
            if not os.path.exists(src):
                time.sleep(0.1)
                continue
            s1 = os.path.getsize(src)
            time.sleep(0.1)
            s2 = os.path.getsize(src)
            if s2 > 0 and s1 == s2:
                break

        # Load image
        img = cv2.imread(src)
        if img is None:
            logger.error(f"Cannot read {src}, deleting")
            safe_remove(src)
            return

        # Enhance image (Sharpen if blurry)
        if is_blurry(img):
            img = sharpen(img)

        # Brightness correction
        if img.mean() < brightness_threshold:
            img = adjust_brightness(img)

        # Resize if needed
        h, w = img.shape[:2]
        if w > resize_width:
            img = cv2.resize(img, (resize_width, int(h * resize_width / w)))

        # **Extract Body Measurements**
        body_measures = extract_body_measurements(img)
        if body_measures:
            logger.info(f"Body Measurements Extracted: {body_measures}")
            match_person = match_body_measurements(body_measures, suspects)
            if match_person:
                logger.info(f"Matched based on body measurements: {match_person}")

        # **Face Detection & Matching**
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb, model=model_type)
        encs = face_recognition.face_encodings(rgb, locs)
        logger.info(f"Detected {len(locs)} face(s)")

        if not encs:
            logger.warning("No faces found, deleting frame")
            safe_remove(src)
            return

        # Match against known suspects
        names, encs_known = zip(*suspects) if suspects else ([], [])
        match, matched_name, matched_distance = False, None, None
        
        for fe in encs:
            dists = face_recognition.face_distance(encs_known, fe)
            i = int(np.argmin(dists))
            logger.debug(f"Distance to {names[i] if names else 'N/A'}: {dists[i]:.3f}")
            if dists[i] < threshold:
                match, matched_name, matched_distance = True, names[i], float(dists[i])
                logger.info(f"Face Matched {matched_name} @ {matched_distance:.3f}")
                break

        # If matched, annotate & save
        if match:
            top, right, bottom, left = locs[0]
            cx, cy = (left+right)//2, (top+bottom)//2
            rad = max((right-left)//2, (bottom-top)//2)
            cv2.circle(img, (cx, cy), rad, (0,255,0), 2)
            cv2.putText(img, ts.strftime("%Y-%m-%d %H:%M:%S"), (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            
            outd = os.path.join(matched_dir, matched_name)
            os.makedirs(outd, exist_ok=True)
            save_path = os.path.join(outd, frame_fn)
            cv2.imwrite(save_path, img)
            logger.info(f"Saved matched image → {save_path}")

            # Log to DB & CSV
            log_to_db(ts, frame_fn, matched_name, matched_distance)
            log_to_csv(ts, frame_fn, matched_name, matched_distance)

        else:
            logger.info("No face match found")

    except Exception as e:
        logger.exception(f"Error in process_frame({frame_fn}): {e}")

    finally:
        safe_remove(src)