import multiprocessing
from camera_utils import run_camera_stream

def start_stream_process(cctv_id, name, stream_url, active_processes):
    process = multiprocessing.Process(
        target=run_camera_stream, 
        args=(cctv_id, name, stream_url), 
        daemon=True
    )
    process.start()
    active_processes[cctv_id] = process
    print(f"[PROCESS STARTED] CCTV {cctv_id}")