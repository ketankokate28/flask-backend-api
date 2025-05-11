# processer_advanced.py
import os
import time
import logging
import numpy as np
import cv2
import torch
import face_recognition
from datetime import datetime
from config import (
    temp_frames, matched_dir, threshold,
    time_window, brightness_threshold, resize_width
)
from image_utils import (
    is_blurry, sharpen, adjust_brightness,
    extract_timestamp
)
from suspect_utils import reload_if_needed
from db_utils import log_to_db
from csv_utils import log_to_csv
# from alert_utils import send_email_alert, send_sms_alert

# Advanced dependencies
from facenet_pytorch import MTCNN
from gfpgan import GFPGANer
from deblurgan_utils import deblur_image  # ensure this file exists alongside processer_advanced.py
from PIL import Image
from torchvision.transforms import ToTensor, ToPILImage

# Initialize models once
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(keep_all=False, device=DEVICE, select_largest=True)
# Correct GFPGANer initialization (specify model_path and parameters)
gfpganer = GFPGANer(
    model_path='GFPGANv1.3.pth',       # local path to the downloaded GFPGANv1.3.pth weights
    upscale=2,
    arch='clean',                     # architecture type: 'clean' or 'original'
    channel_multiplier=2,
    bg_upsampler=None,
    device=DEVICE
)
to_pil = ToPILImage()

logger = logging.getLogger(__name__)

def gamma_correction(image: np.ndarray, gamma: float = 0.67) -> np.ndarray:
    """Apply gamma correction to boost midtones."""
    inv = 1.0 / gamma
    table = np.array([((i/255.0) ** inv) * 255 for i in np.arange(256)], dtype='uint8')
    return cv2.LUT(image, table)


def align_face(image: np.ndarray) -> np.ndarray:
    """Use MTCNN to align the largest detected face."""
    pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    aligned = mtcnn(pil)
    if aligned is not None:
        return cv2.cvtColor(np.array(to_pil(aligned)), cv2.COLOR_RGB2BGR)
    return image


def safe_remove(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def process_frame_advanced(frame_fn: str):
    """
    Enhanced pipeline with debug image saving:
    Saves original, aligned, restored, and pre-match images for inspection.
    """
    src = os.path.join(temp_frames, frame_fn)
    logger.info(f"[ADV] Processing frame: {frame_fn}")
    debug_dir = os.path.join(temp_frames, 'debug')
    os.makedirs(debug_dir, exist_ok=True)

    try:
        suspects = reload_if_needed()
        ts = extract_timestamp(frame_fn)

        # 1) Drop too-old
        if ts < datetime.now() - time_window:
            safe_remove(src)
            return

        # 2) Wait until file write completes
        for _ in range(5):
            if os.path.exists(src) and os.path.getsize(src) > 0:
                break
            time.sleep(0.1)

        # 3) Load
        img = cv2.imread(src)
        if img is None:
            safe_remove(src)
            return

        # Debug: save original
        orig_path = os.path.join(debug_dir, f'orig_{frame_fn}')
        cv2.imwrite(orig_path, img)
        logger.debug(f"Saved original → {orig_path}")

        # 4) Sharpen
        if is_blurry(img):
            img = sharpen(img)

        # 5) Brightness
        if img.mean() < brightness_threshold:
            img = adjust_brightness(img)
            img = cv2.convertScaleAbs(img, alpha=1.0, beta=50)

        # 6) Denoise + gamma
        img = cv2.bilateralFilter(img, d=5, sigmaColor=75, sigmaSpace=75)
        img = gamma_correction(img)

        # 7) Align
        img = align_face(img)
        aligned_path = os.path.join(debug_dir, f'aligned_{frame_fn}')
        cv2.imwrite(aligned_path, img)
        logger.debug(f"Saved aligned → {aligned_path}")

        # 8) Super-res & deblur
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, restored = gfpganer.enhance(rgb, has_aligned=True, only_center_face=True)
        if restored is not None:
            img = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)
        img = deblur_image(img)
        restored_path = os.path.join(debug_dir, f'restored_{frame_fn}')
        cv2.imwrite(restored_path, img)
        logger.debug(f"Saved restored → {restored_path}")

        # 9) Resize
        h, w = img.shape[:2]
        if w > resize_width:
            img = cv2.resize(img, (resize_width, int(h * resize_width / w)))

        # 10) Detect + encode
        rgb2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb2, model='cnn')
        encs = face_recognition.face_encodings(rgb2, locs)
        if not encs:
            safe_remove(src)
            return

        # 11) Match
        names, encs_known = zip(*suspects) if suspects else ([], [])
        match, mname, md = False, None, None
        for fe in encs:
            dists = face_recognition.face_distance(encs_known, fe)
            idx = int(np.argmin(dists))
            if dists[idx] < threshold:
                match, mname, md = True, names[idx], float(dists[idx])
                break

        # Debug: save pre-match
        pre_match = os.path.join(debug_dir, f'pre_match_{frame_fn}')
        cv2.imwrite(pre_match, img)
        logger.debug(f"Saved pre-match → {pre_match}")

        # 12) Annotate, save & log
        if match:
            top, right, bottom, left = locs[0]
            cv2.circle(img, ((left+right)//2, (top+bottom)//2),
                       max((right-left)//2, (bottom-top)//2), (0,255,0), 2)
            cv2.putText(img, ts.strftime('%Y-%m-%d %H:%M:%S'), (10,25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            outd = os.path.join(matched_dir, mname)
            os.makedirs(outd, exist_ok=True)
            cv2.imwrite(os.path.join(outd, frame_fn), img)
            log_to_db(ts, frame_fn, mname, md)
            log_to_csv(ts, frame_fn, mname, md)

    except Exception as e:
        logger.exception(f"[ADV] Error processing {frame_fn}: {e}")
    finally:
        safe_remove(src)
