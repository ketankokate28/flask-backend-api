from ultralytics import YOLO

def initialize_yolo(model_path):
    try:
        return YOLO(model_path)
    except Exception as e:
        print(f"[YOLO INIT ERROR] {e}")
        return None

def process_frame_with_yolo(frame, model):
    results = []
    try:
        predictions = model(frame)
        for prediction in predictions:
            boxes = prediction.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if cls_id == 0 and conf > 0.3:  # Example: Detect only class "person"
                    results.append({"class_id": cls_id, "confidence": conf})
    except Exception as e:
        print(f"[YOLO PROCESSING ERROR] {e}")
    return results