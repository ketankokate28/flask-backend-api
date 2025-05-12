# processor.py (with email, SMS, and call alerts)
import os
import time
import logging
import numpy as np
import cv2
import face_recognition

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
from alert_utils import send_email_alert, send_sms_alert, send_call_alert

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
    """
    Safely remove a file, ignoring if it doesn't exist.
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        logger.debug(f"No file to remove: {path}")


def process_frame(frame_fn: str):
    """
    Process a single frame with full pipeline and alerts.
    """
    src = os.path.join(temp_frames, frame_fn)
    logger.info(f"Processing frame: {frame_fn}")

    try:
        # Reload current suspects (id, name, encoding)
        suspects = reload_if_needed()
        # If no suspects, skip processing
        if not suspects:
            logger.warning("No suspects available; skipping this frame")
            safe_remove(src)
            return

        # Extract timestamp
        ts = extract_timestamp(frame_fn)

        # Drop too-old frames
        if ts < datetime.now() - time_window:
            logger.warning(f"Frame too old ({ts}), deleting")
            safe_remove(src)
            return

        # Wait until file is fully written
        for _ in range(5):
            if not os.path.exists(src):
                time.sleep(0.1)
                continue
            if os.path.getsize(src) > 0:
                break
            time.sleep(0.1)

        # Load image
        img = cv2.imread(src)
        if img is None:
            logger.error(f"Cannot read {src}, deleting")
            safe_remove(src)
            return

        # Image preprocessing
        if is_blurry(img):
            img = sharpen(img)
        if img.mean() < brightness_threshold:
            debug_dir = os.path.join(temp_frames, "debug")
            os.makedirs(debug_dir, exist_ok=True)
            cv2.imwrite(os.path.join(debug_dir, f"before_{frame_fn}"), img)
            img = adjust_brightness(img)
            img = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
            cv2.imwrite(os.path.join(debug_dir, f"after_{frame_fn}"), img)

        # Resize if needed
        h, w = img.shape[:2]
        if w > resize_width:
            new_h = int(h * resize_width / w)
            img = cv2.resize(img, (resize_width, new_h))

        # Face detection & encoding
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb, model=model_type, number_of_times_to_upsample=2)
        encs = face_recognition.face_encodings(rgb, locs)
        logger.info(f"Detected {len(locs)} face(s)")

        # Remove temp frame immediately after encoding
        safe_remove(src)
        if not encs:
            return

        # Prepare suspect lists
        ids, names, encs_known = zip(*suspects)

        # Match against suspects
        match = False
        for fed in encs:
            dists = face_recognition.face_distance(encs_known, fed)
            idx = int(np.argmin(dists))
            if dists[idx] < threshold:
                match = True
                suspect_id = ids[idx]
                suspect_name = names[idx]
                distance = float(dists[idx])
                logger.info(f"Matched {suspect_name} @ {distance:.3f}")
                break

        # On match: annotate, save, log, and send alerts
        if match:
            top, right, bottom, left = locs[0]
            cx, cy = (left+right)//2, (top+bottom)//2
            rad = max((right-left)//2, (bottom-top)//2)
            cv2.circle(img, (cx, cy), rad, (0,255,0), 2)
            cv2.putText(img, ts.strftime("%Y-%m-%d %H:%M:%S"), (10,25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            out_dir = os.path.join(matched_dir, suspect_name)
            os.makedirs(out_dir, exist_ok=True)
            save_path = os.path.join(out_dir, frame_fn)
            cv2.imwrite(save_path, img)

           
            # TODO: derive camera_id from frame_fn prefix or metadata
            cctv_id = None
            prefix = frame_fn.split('_', 1)[0]  # e.g., "CAM2"
            if prefix.startswith("CAM"):
                try:
                    cctv_id = int(prefix[3:])
                except ValueError:
                    cctv_id = None
            else:
                cctv_id = None
                 # Log to DB & CSV
            log_to_db(ts, frame_fn, cctv_id, suspect_id,suspect_name, distance)
            log_to_csv(ts, frame_fn,cctv_id, suspect_id, suspect_name, distance)

            # Send alerts
            send_email_alert(frame_fn, suspect_name, distance, cctv_id, suspect_id)
            #send_sms_alert(frame_fn, suspect_name, camera_id, suspect_id)
            #send_call_alert(frame_fn, suspect_name, camera_id, suspect_id)

    except Exception as e:
        logger.exception(f"Error processing {frame_fn}: {e}")
    finally:
        # Ensure temp frame is removed if not already
        safe_remove(src)
