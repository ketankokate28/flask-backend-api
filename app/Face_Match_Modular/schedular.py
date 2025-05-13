# scheduler.py
"""
Standalone scheduler to run two jobs at specified intervals:
  - record_new(): inserts pending notifications every minute
  - dispatch(): sends pending notifications every 2 minutes
"""
import time
import logging
import os
from record_notifications import record_new
from dispatch_notifications import dispatch
from flask import Flask
from db_models import db
from app_scheduler import create_app

# Optional: configure logging to file
generic_log = os.path.join(os.path.dirname(__file__), 'scheduler.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(generic_log),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Simple scheduling using time.sleep loop
def run_scheduler():
    last_record_time = 0
    last_dispatch_time = 0
    record_interval = 60     # seconds
    dispatch_interval = 120  # seconds

    logger.info("Scheduler started: record every %ds, dispatch every %ds",
                record_interval, dispatch_interval)
    try:
        while True:
            now = time.time()
            # Job A: record_new every record_interval
            if now - last_record_time >= record_interval:
                logger.info("Running record_new() job")
                try:
                    record_new()
                except Exception as e:
                    logger.exception("Error in record_new: %s", e)
                last_record_time = now

            # Job B: dispatch every dispatch_interval
            if now - last_dispatch_time >= dispatch_interval:
                logger.info("Running dispatch() job")
                try:
                    dispatch()
                except Exception as e:
                    logger.exception("Error in dispatch: %s", e)
                last_dispatch_time = now

            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        run_scheduler()
