import cv2
import json
import time
import os
from ultralytics import YOLO
from datetime import datetime
from config import CAMERAS
from arcgis_update import update_camera

model = YOLO("yolov8s.pt")
VEHICLE_CLASSES = [2, 3, 5, 7]
INTERVAL = 60  # sekundi između analiza

def calculate_status(traffic_score):
    if traffic_score < 30:
        return "protočno"
    elif traffic_score < 60:
        return "usporeno"
    else:
        return "velika gužva"

def calculate_traffic_score(vehicle_count):
    # Maksimum koji očekujemo u kadru je 50 vozila
    MAX_VEHICLES = 50
    score = min(int((vehicle_count / MAX_VEHICLES) * 100), 100)
    return score

def analyze_camera(camera):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Analiziram: {camera['location']}")

    cap = cv2.VideoCapture(camera['stream_url'])
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"✗ Nije moguće čitati stream: {camera['location']}")
        return

    results = model(frame, conf=0.15, verbose=False)

    vehicle_count = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls) in VEHICLE_CLASSES:
                vehicle_count += 1

    traffic_score = calculate_traffic_score(vehicle_count)
    status = calculate_status(traffic_score)

    print(f"  Vozila: {vehicle_count} | Score: {traffic_score} | Status: {status}")

    update_camera(camera['camera_id'], vehicle_count, traffic_score, status)

def run():
    print("🚦 TrafficLens AI — worker pokrenut")
    print(f"   Kamere: {len(CAMERAS)}")
    print(f"   Interval: {INTERVAL}s")
    print("-" * 40)

    while True:
        for camera in CAMERAS:
            analyze_camera(camera)
        print(f"\n⏳ Sledeća analiza za {INTERVAL}s...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    run()