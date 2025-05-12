# deblurgan_utils.py
import cv2
import numpy as np

def deblur_image(image: np.ndarray) -> np.ndarray:
    """
    Basic deblurring stub using an unsharp mask.

    Replace this stub with a true DeblurGAN model inference if desired.
    """
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=3)
    # Unsharp mask: combine original and blurred image
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
    return sharpened
    