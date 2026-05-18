# capture_frame.py
import cv2
from config import CAMERAS

for camera in CAMERAS:
    print(f"Povezujem se na {camera['location']}...")
    cap = cv2.VideoCapture(camera['stream_url'])
    ret, frame = cap.read()

    if ret:
        filename = f"frame_{camera['camera_id']}.jpg"
        cv2.imwrite(filename, frame)
        print(f"✓ Frame sačuvan: {filename}")
    else:
        print(f"✗ Nije moguće čitati stream: {camera['location']}")

    cap.release()