import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

FEATURE_SERVICE_URL = os.getenv("ARCGIS_FEATURE_SERVICE_URL")

def get_token():
    response = requests.post(
        os.getenv("ARCGIS_TOKEN_URL"),
        data={
            "username": os.getenv("ARCGIS_USERNAME"),
            "password": os.getenv("ARCGIS_PASSWORD"),
            "client": "referer",
            "referer": "http://localhost",
            "expiration": 60,
            "f": "json"
        }
    )
    data = response.json()
    if "token" in data:
        return data["token"]
    else:
        print(f"✗ Greška pri generisanju tokena: {data}")
        return None

def get_object_id(camera_id, token):
    url = f"{FEATURE_SERVICE_URL}/0/query"
    params = {
        "where": f"camera_id='{camera_id}'",
        "outFields": "OBJECTID",
        "f": "json",
        "token": token
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("features"):
        return data["features"][0]["attributes"]["OBJECTID"]
    return None

def update_camera(camera_id, vehicle_count, traffic_score, status):
    token = get_token()
    if not token:
        return

    object_id = get_object_id(camera_id, token)
    if not object_id:
        print(f"✗ Nije pronađena kamera {camera_id}")
        return

    url = f"{FEATURE_SERVICE_URL}/0/updateFeatures"
    features = [{
        "attributes": {
            "OBJECTID": object_id,
            "vehicle_count": vehicle_count,
            "traffic_score": traffic_score,
            "status": status,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }]

    response = requests.post(url, data={
        "features": json.dumps(features),
        "f": "json",
        "token": token
    })
    data = response.json()

    if data.get("updateResults") and data["updateResults"][0].get("success"):
        print(f"✓ Kamera {camera_id} ažurirana: {vehicle_count} vozila, score {traffic_score}, status: {status}")
    else:
        print(f"✗ Greška pri ažuriranju: {data}")

def test_connection():
    token = get_token()
    if not token:
        return
    url = f"{FEATURE_SERVICE_URL}/0/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "json",
        "token": token
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "features" in data:
        print(f"✓ Konekcija uspešna! Pronađeno {len(data['features'])} kamera:")
        for feature in data["features"]:
            attrs = feature["attributes"]
            print(f"  - {attrs.get('location')} (camera_id: {attrs.get('camera_id')})")
    else:
        print(f"✗ Greška: {data}")

if __name__ == "__main__":
    test_connection()