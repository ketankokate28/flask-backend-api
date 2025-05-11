# suspect_utils.py
import os
import logging
import face_recognition
from datetime import datetime
import sqlite3
import numpy as np
import json
from config import suspect_dir, suspect_refresh

DB_PATH = 'D:/Face_Detect/flask-backend-api/database/face_match.db'

logger = logging.getLogger(__name__)
suspects = []
_last_refresh = datetime.min

def init_suspects():
    global suspects, _last_refresh
    suspects = _load_from_folder() #_load_from_database()
    _last_refresh = datetime.now()
    logger.info(f"Loaded {len(suspects)} suspects")
    return suspects


def _load_from_folder():
    lst = []
    for fn in os.listdir(suspect_dir):
        if fn.lower().endswith(('jpg','jpeg','png')):
            path = os.path.join(suspect_dir, fn)
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if encs:
                lst.append((os.path.splitext(fn)[0], encs[0]))
                logger.debug(f"Encoded suspect: {fn}")
    return lst


def reload_if_needed():
    global suspects, _last_refresh
    if datetime.now() - _last_refresh > suspect_refresh:
        suspects =_load_from_folder() #_load_from_database()#
        _last_refresh = datetime.now()
        logger.info(f"Reloaded suspects, count: {len(suspects)}")
    return suspects


def _load_from_database():
    lst = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT suspect_id, first_name || ' ' || last_name AS Name,file_blob FROM suspects;")

        for name, encoding in cursor.fetchall():
            enc_array = np.array(json.loads(encoding))  # Convert JSON string to NumPy array
            lst.append((name, enc_array))
            logger.debug(f"Loaded suspect: {name}")

        conn.close()
    except Exception as e:
        logger.error(f"Error loading suspects from database: {e}")
    
    return lst

# Replace _load_from_folder() with _load_from_database() in init_suspects() and reload_if_needed()
