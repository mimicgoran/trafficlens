# test_yolo.py
from ultralytics import YOLO
import cv2
from config import CAMERAS

model = YOLO("yolov8s.pt")

for camera in CAMERAS:
    filename = f"frame_{camera['camera_id']}.jpg"
    frame = cv2.imread(filename)

    if frame is None:
        print(f"Nema frame-a za kameru {camera['camera_id']} — pokreni capture_frame.py prvo")
        continue

    results = model(frame, conf=0.15, verbose=False)

    vehicle_classes = [2, 3, 5, 7]
    vehicle_count = 0

    for result in results:
        for box in result.boxes:
            if int(box.cls) in vehicle_classes:
                vehicle_count += 1

    print(f"Kamera {camera['camera_id']} ({camera['location']}): detektovano {vehicle_count} vozila")

    annotated = results[0].plot()
    cv2.imwrite(f"detected_{camera['camera_id']}.jpg", annotated)
    print(f"Sačuvana slika: detected_{camera['camera_id']}.jpg")