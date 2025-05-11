# processor.py
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
# from alert_utils import send_email_alert, send_sms_alert

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
    Process a single frame:
      1) Validate timestamp
      2) Ensure file write completion
      3) Load image
      4) Sharpen if blurry
      5) Boost brightness if too dark, saving before/after debug images
      6) Resize if needed
      7) Detect & encode faces
      8) Match against suspects
      9) Annotate, save, log on match
     10) Clean up temp file
    """
    src = os.path.join(temp_frames, frame_fn)
    logger.info(f"Processing frame: {frame_fn}")

    try:
        # Reload current suspects (name, encoding)
        suspects = reload_if_needed()
        # Extract timestamp from filename
        ts = extract_timestamp(frame_fn)

        # 1) Drop too-old frames
        if ts < datetime.now() - time_window:
            logger.warning(f"Frame too old ({ts}), deleting")
            safe_remove(src)
            return

        # 2) Wait until file is fully written
        for _ in range(5):
            if not os.path.exists(src):
                time.sleep(0.1)
                continue
            s1 = os.path.getsize(src)
            time.sleep(0.1)
            s2 = os.path.getsize(src)
            if s2 > 0 and s1 == s2:
                break

        # 3) Load image
        img = cv2.imread(src)
        if img is None:
            logger.error(f"Cannot read {src}, deleting")
            safe_remove(src)
            return

        # 4) If blurry, sharpen
        if is_blurry(img):
            logger.debug("Image is blurry → applying sharpen()")
            img = sharpen(img)

        # 5) If too dark, boost brightness and save debug images
        if img.mean() < brightness_threshold:
            logger.debug(f"Image too dark (mean={img.mean():.1f}) → boosting brightness")
            # Debug directory
            debug_dir = os.path.join(temp_frames, "debug")
            print("debug_dir:",debug_dir)
            os.makedirs(debug_dir, exist_ok=True)
            # Save before-brightness image
            before_path = os.path.join(debug_dir, f"before_{frame_fn}")
            cv2.imwrite(before_path, img)
            logger.debug(f"Saved pre-brightness debug image → {before_path}")

            # Apply CLAHE brightness adjustment
            img = adjust_brightness(img)
            # Apply additive brightness boost
            img = cv2.convertScaleAbs(img, alpha=1.0, beta=50)

            # Save after-brightness image
            after_path = os.path.join(debug_dir, f"after_{frame_fn}")
            cv2.imwrite(after_path, img)
            logger.debug(f"Saved post-brightness debug image → {after_path}")

        # 6) Resize if width exceeds limit
        h, w = img.shape[:2]
        if w > resize_width:
            new_h = int(h * resize_width / w)
            img = cv2.resize(img, (resize_width, new_h))
            logger.debug(f"Resized to {resize_width}×{new_h}")

        # 7) Face detection & encoding
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb, model=model_type,number_of_times_to_upsample=2)
        encs = face_recognition.face_encodings(rgb, locs)
        logger.info(f"Detected {len(locs)} face(s)")

        if not encs:
            logger.warning("No faces found, deleting frame")
            safe_remove(src)
            return

        # 8) Match against each encoding
        names, encs_known = zip(*suspects) if suspects else ([], [])
        match, mname, md = False, None, None
        for fe in encs:
            dists = face_recognition.face_distance(encs_known, fe)
            i = int(np.argmin(dists))
            logger.debug(f"Distance to {names[i] if names else 'N/A'}: {dists[i]:.3f}")
            if dists[i] < threshold:
                match, mname, md = True, names[i], float(dists[i])
                logger.info(f"Matched {mname} @ {md:.3f}")
                break

        # 9) On match, annotate & save & log
        if match:
            top, right, bottom, left = locs[0]
            cx, cy = (left+right)//2, (top+bottom)//2
            rad = max((right-left)//2, (bottom-top)//2)
            cv2.circle(img, (cx, cy), rad, (0,255,0), 2)
            cv2.putText(
                img,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2
            )
            outd = os.path.join(matched_dir, mname)
            os.makedirs(outd, exist_ok=True)
            save_path = os.path.join(outd, frame_fn)
            cv2.imwrite(save_path, img)
            logger.info(f"Saved matched image → {save_path}")

            # Log to DB & CSV
            log_to_db(ts, frame_fn, mname, md)
            log_to_csv(ts, frame_fn, mname, md)
            # send_email_alert(frame_fn, mname, md)
            # send_sms_alert(frame_fn, mname)

        else:
            logger.info("No match found")

    except Exception as e:
        logger.exception(f"Error in process_frame({frame_fn}): {e}")

    finally:
        # 10) Always remove source frame
        safe_remove(src)