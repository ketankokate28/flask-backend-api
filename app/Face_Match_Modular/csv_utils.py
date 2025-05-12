# csv_utils.py
import os
import csv
import logging
from config import csv_log

logger = logging.getLogger(__name__)

def init_csv():
    if not os.path.exists(csv_log):
        with open(csv_log, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["capture_time", "frame", "suspect", "distance"])
        logger.info(f"CSV log created: {csv_log}")
    else:
        logger.info(f"CSV log exists: {csv_log}")


def log_to_csv(capture_ts, frame, suspect, distance,cctv_id, suspect_id):
    try:
        with open(csv_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([capture_ts.isoformat(), frame,cctv_id, suspect_id, suspect, distance])
        logger.debug(f"Logged to CSV: {frame}, {suspect}, {distance:.3f}")
    except Exception:
        logger.exception("Failed to log to CSV")
