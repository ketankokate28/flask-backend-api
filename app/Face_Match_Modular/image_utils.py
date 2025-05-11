# image_utils.py
import cv2
import numpy as np
import re
from datetime import datetime

from config import blur_threshold, brightness_threshold

def is_blurry(image: np.ndarray) -> bool:
    """Return True if variance of Laplacian is below our blur threshold."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    var  = cv2.Laplacian(gray, cv2.CV_64F).var()
    return var < blur_threshold

def sharpen(image: np.ndarray) -> np.ndarray:
    """Unsharp mask: boost edge by adding weighted difference back."""
    blur = cv2.GaussianBlur(image, (0,0), sigmaX=3)
    return cv2.addWeighted(image, 1.5, blur, -0.5, 0)

def adjust_brightness(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
    """
    Boost dark images via CLAHE on the V channel of HSV.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8,8))
    v2 = clahe.apply(v)
    hsv2 = cv2.merge((h, s, v2))
    return cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)

_TIMESTAMP_RE = re.compile(r".*?(\d{4})(\d{2})(\d{2})[_-]?(\d{2})(\d{2})(\d{2})")

def extract_timestamp(filename: str) -> datetime:
    """
    Parse a timestamp out of filenames like:
      'frame_20250429_221530.jpg' or '20250429-221530.png'
    """
    m = _TIMESTAMP_RE.match(filename)
    if not m:
        # fallback to now()
        return datetime.now()
    year, month, day, hh, mm, ss = map(int, m.groups())
    return datetime(year, month, day, hh, mm, ss)
