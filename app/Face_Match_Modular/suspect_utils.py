# suspect_utils_sqlalchemy_refactored.py
"""
Refactored suspect utilities using SuspectStore for all CRUD,
plus caching and embedding via SQLAlchemy ORM.
"""
import logging
import base64
from datetime import datetime
import numpy as np
import cv2
import face_recognition

from config import suspect_refresh
from db_store.suspect_store import SuspectStore

logger = logging.getLogger(__name__)

# Global cache for embeddings
global_suspects = []  # List of tuples: (id, full_name, embedding)
_last_refresh = datetime.min


def init_suspects():
    """
    Load all suspects into the cache (decoding images + computing embeddings).
    """
    global global_suspects, _last_refresh
    global_suspects = _load_embeddings()
    _last_refresh = datetime.now()
    logger.info(f"Loaded {len(global_suspects)} suspects via SuspectStore")
    return global_suspects


def reload_if_needed():
    """Reload cache if refresh interval has passed."""
    global global_suspects, _last_refresh
    if datetime.now() - _last_refresh > suspect_refresh:
        global_suspects = _load_embeddings()
        _last_refresh = datetime.now()
        logger.info(f"Reloaded {len(global_suspects)} suspects via SuspectStore")
    return global_suspects


def _load_embeddings():
    """
    Internal: fetch suspects via SuspectStore, decode image BLOBs, compute face embeddings.
    Returns list of (suspect_id, full_name, embedding_array).
    """
    suspects_list = []
    # Fetch all suspects
    records = SuspectStore.get_all()
    for rec in records:
        if not rec.file_blob:
            continue
        try:
            # Decode Base64 blob
            raw = base64.b64decode(rec.file_blob) if isinstance(rec.file_blob, str) else rec.file_blob
            # Convert bytes -> numpy -> OpenCV image
            arr = np.frombuffer(raw, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                logger.error(f"Failed to decode image for suspect {rec.id}")
                continue
            # Face embedding
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encs = face_recognition.face_encodings(rgb)
            if not encs:
                logger.warning(f"No face found in suspect image {rec.id}")
                continue
            embedding = encs[0]
            full_name = f"{rec.first_name} {rec.last_name}"
            suspects_list.append((rec.id, full_name, embedding))
            logger.debug(f"Loaded embedding for suspect {rec.id}")
        except Exception as e:
            logger.error(f"Error processing suspect {rec.id}: {e}")
    return suspects_list

# CRUD wrappers using SuspectStore

def create_suspect(form_data, image_file):
    """Create a new suspect record via SuspectStore."""
    return SuspectStore.create(form_data, image_file)


def get_all_suspects():
    """Return list of all Suspect ORM objects."""
    return SuspectStore.get_all()


def get_suspect_by_id(suspect_id):
    """Fetch one Suspect by ID."""
    return SuspectStore.get_by_id(suspect_id)


def update_suspect(suspect_id, form_data, image_file=None):
    """Update an existing suspect."""
    return SuspectStore.update(suspect_id, form_data, image_file)


def delete_suspect(suspect_id):
    """Delete a suspect by ID."""
    return SuspectStore.delete(suspect_id)
