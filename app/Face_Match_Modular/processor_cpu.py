# processor_cpu.py
import os
import time
import logging
import numpy as np
import cv2
from datetime import datetime
from config import (
    temp_frames,
    matched_dir,
    threshold,
    resize_width,
    time_window,
    brightness_threshold
)
from image_utils import is_blurry, sharpen, extract_timestamp
from suspect_utils import reload_if_needed
from db_utils import log_to_db
from csv_utils import log_to_csv
from deepface import DeepFace

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Pre-load your recognition model once for CPU use
# Use 'Facenet' or 'ArcFace' as model_name, and default 'retinaface' backend
RECOGNITION_MODEL = DeepFace.build_model('Facenet')  # builds on CPU by default

# Helper to get embeddings from an image array
def get_embeddings(img: np.ndarray) -> list[np.ndarray]:
    # DeepFace expects BGR or RGB? It auto-converts if given array
    # enforce_detection=True ensures failure if no face
    reps = DeepFace.represent(
        img_path = None,
        img = img,
        model = RECOGNITION_MODEL,
        enforce_detection = True,
        detector_backend = 'retinaface',
        align = True
    )
    # reps is list of dicts or a single dict
    if isinstance(reps, dict):
        reps = [reps]
    return [np.array(r['embedding']) for r in reps]

# Main CPU-only frame processing
def process_frame_cpu(frame_fn: str):
    """
    CPU-only face matching pipeline with debug snapshots:
      1) Timestamp & freshness check
      2) File readiness
      3) Load image
      4) Sharpen if blurry
      5) Brightness boost if too dark (and save before/after)
      6) Resize
      7) Extract embeddings via DeepFace (retinaface + Facenet) on CPU
      8) Compare to suspects
      9) Annotate & save if match
     10) Clean up temp frame
    """
    src = os.path.join(temp_frames, frame_fn)
    logger.info(f"[CPU] Processing frame: {frame_fn}")

    # Prepare debug output
    debug_dir = os.path.join(temp_frames, 'debug_cpu')
    os.makedirs(debug_dir, exist_ok=True)

    try:
        # Reload suspects: list of (name, encoding np.ndarray)
        suspects = reload_if_needed()
        ts = extract_timestamp(frame_fn)

        # 1) Drop frames older than time_window
        if ts < datetime.now() - time_window:
            logger.warning("Frame too old, deleting")
            os.remove(src)
            return

        # 2) Wait for file write completion
        for _ in range(5):
            if os.path.exists(src) and os.path.getsize(src) > 0:
                break
            time.sleep(0.1)

        # 3) Load BGR image
        img = cv2.imread(src)
        if img is None:
            logger.error("Failed to read image, deleting")
            os.remove(src)
            return

        # Debug: save original copy
        cv2.imwrite(os.path.join(debug_dir, f"orig_{frame_fn}"), img)

        # 4) Sharpen if blurry
        if is_blurry(img):
            logger.debug("Blurry image detected, sharpening")
            img = sharpen(img)

        # 5) Brightness boost
        #if img.mean() < brightness_threshold:
            logger.debug("Low brightness, boosting")
            before = img.copy()
            cv2.imwrite(os.path.join(debug_dir, f"before_{frame_fn}"), before)

            # equalize histogram on V channel
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v_eq = cv2.equalizeHist(v)
            hsv = cv2.merge([h, s, v_eq])
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Additive boost
            img = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
            cv2.imwrite(os.path.join(debug_dir, f"after_{frame_fn}"), img)

        # 6) Resize if too large
        h, w = img.shape[:2]
        if w > resize_width:
            new_h = int(h * resize_width / w)
            img = cv2.resize(img, (resize_width, new_h))

        # 7) Face embeddings on CPU
        try:
            embeddings = get_embeddings(img)
        except ValueError as e:
            logger.warning("No face detected by DeepFace, deleting")
            os.remove(src)
            return

        # 8) Match logic
        names, encs_known = zip(*suspects) if suspects else ([], [])
        match, mname, md = False, None, None
        for fe in embeddings:
            dists = np.linalg.norm(np.stack(encs_known) - fe, axis=1)
            idx = int(np.argmin(dists))
            if dists[idx] < threshold:
                match, mname, md = True, names[idx], float(dists[idx])
                logger.info(f"Matched {mname} (dist={md:.3f})")
                break

        # 9) Annotate & save
        if match:
            # simple draw: circle center of image
            cx, cy = img.shape[1]//2, img.shape[0]//2
            rad = min(cx, cy) // 2
            cv2.circle(img, (cx, cy), rad, (0,255,0), 2)
            cv2.putText(img, ts.strftime('%Y-%m-%d %H:%M:%S'), (10,25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            outd = os.path.join(matched_dir, mname)
            os.makedirs(outd, exist_ok=True)
            cv2.imwrite(os.path.join(outd, frame_fn), img)

            # log
            log_to_db(ts, frame_fn, mname, md)
            log_to_csv(ts, frame_fn, mname, md)
        else:
            logger.info("No match found")

    except Exception as e:
        logger.exception(f"[CPU] Error processing {frame_fn}: {e}")
    finally:
        # 10) Clean up temp file
        try:
            os.remove(src)
        except FileNotFoundError:
            pass
