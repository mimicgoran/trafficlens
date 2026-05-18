import requests

response = requests.post(
    "https://mimic.maps.arcgis.com/sharing/rest/generateToken",
    data={
        "username": "mimic011",
        "password": "Irris9344..",
        "client": "referer",
        "referer": "http://localhost",
        "expiration": 60,
        "f": "json"
    }
)
print(response.json())