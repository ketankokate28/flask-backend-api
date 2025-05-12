# suspect_utils_sqlalchemy.py
"""
Revised suspect_utils using SQLAlchemy ORM and handling Base64-encoded image BLOBs.
"""
import logging
import base64
from datetime import datetime
import numpy as np
import cv2
import face_recognition
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from config import suspect_refresh, db_path  # ensure DB_PATH refers to your SQLite file

logger = logging.getLogger(__name__)
Base = declarative_base()

class Suspect(Base):
    __tablename__ = 'suspects'
    suspect_id     = Column(Integer, primary_key=True)
    first_name     = Column(String, nullable=False)
    last_name      = Column(String, nullable=False)
    file_blob      = Column(LargeBinary, nullable=True)  # may contain Base64 str bytes or raw blob

# Create engine and session factory
engine = create_engine(f"sqlite:///{db_path}?check_same_thread=False", echo=False)
Session = sessionmaker(bind=engine)

# Global cache
global_suspects = []
_last_refresh = datetime.min

def init_suspects():
    """
    Load all suspects from the database into a global cache, decoding images and computing embeddings.
    Returns:
        List of tuples: (suspect_id, full_name, embedding_array)
    """
    global global_suspects, _last_refresh
    global_suspects = _load_from_database()
    _last_refresh = datetime.now()
    logger.info(f"Loaded {len(global_suspects)} suspects via SQLAlchemy and Base64 decode")
    return global_suspects


def reload_if_needed():
    """
    Reload suspects if the configured refresh interval has elapsed.
    """
    global global_suspects, _last_refresh
    if datetime.now() - _last_refresh > suspect_refresh:
        global_suspects = _load_from_database()
        _last_refresh = datetime.now()
        logger.info(f"Reloaded {len(global_suspects)} suspects via SQLAlchemy and Base64 decode")
    return global_suspects


def _load_from_database():
    """
    Internal: Query the suspects table via SQLAlchemy, decode Base64 image data, and compute embeddings.
    Expects file_blob as Base64-encoded image bytes. Returns list of tuples: (suspect_id, full_name, embedding_array)
    """
    session = Session()
    suspects_list = []
    try:
        # Fetch only suspects with non-null file_blob
        records = session.query(Suspect).filter(Suspect.file_blob.isnot(None)).all()
        for rec in records:
            try:
                # Determine raw bytes
                raw = None
                # If file_blob is text (Base64), decode
                if isinstance(rec.file_blob, (bytes, bytearray, memoryview)):
                    # Could be Base64 string bytes or raw image bytes
                    try:
                        # Try to interpret as Base64 string
                        b64_str = rec.file_blob.decode('utf-8')
                        raw = base64.b64decode(b64_str)
                    except Exception:
                        # Fallback: treat file_blob as raw image bytes
                        raw = bytes(rec.file_blob)
                elif isinstance(rec.file_blob, str):
                    raw = base64.b64decode(rec.file_blob)
                else:
                    logger.error(f"Unsupported file_blob type for suspect {rec.suspect_id}: {type(rec.file_blob)}")
                    continue

                # Convert raw image bytes into OpenCV image
                arr = np.frombuffer(raw, dtype=np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if img is None:
                    logger.error(f"Failed to decode image for suspect {rec.suspect_id}")
                    continue

                # Compute face embedding
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encs = face_recognition.face_encodings(rgb)
                if not encs:
                    logger.warning(f"No face found in suspect image {rec.suspect_id}")
                    continue
                embedding = encs[0]

                full_name = f"{rec.first_name} {rec.last_name}"
                suspects_list.append((rec.suspect_id, full_name, embedding))
                logger.debug(f"Loaded suspect {rec.suspect_id}: {full_name}")
            except Exception as e:
                logger.error(f"Error processing suspect {rec.suspect_id}: {e}")
    except Exception as e:
        logger.error(f"Database query failed: {e}")
    finally:
        session.close()
    return suspects_list
