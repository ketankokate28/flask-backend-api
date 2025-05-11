# run_matcher.py
import os
import time
import logging
from concurrent.futures import ProcessPoolExecutor
from config import temp_frames, matched_dir, workers, check_interval
from db_utils import init_db
from csv_utils import init_csv
from suspect_utils import init_suspects
from processor import process_frame 

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting face recognition matcher")
    init_db()
    init_csv()
    init_suspects()
    os.makedirs(matched_dir, exist_ok=True)

    with ProcessPoolExecutor(max_workers=workers) as pool:
        while True:
            try:
                frames = [f for f in os.listdir(temp_frames)
                          if f.lower().endswith(('jpg','png','jpeg'))]
                if frames:
                    logger.info(f"Found {len(frames)} frames, dispatching...")
                    pool.map(process_frame, frames)
                time.sleep(check_interval)
            except Exception:
                logger.exception("Error in run_matcher loop")
