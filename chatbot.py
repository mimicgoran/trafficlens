import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

FEATURE_SERVICE_URL = os.getenv("ARCGIS_FEATURE_SERVICE_URL")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    return data.get("token")


def get_traffic_data():
    token = get_token()
    url = f"{FEATURE_SERVICE_URL}/0/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "json",
        "token": token
    }
    response = requests.get(url, params=params)
    data = response.json()

    kamere = []
    for feature in data["features"]:
        attrs = feature["attributes"]
        kamere.append({
            "location": attrs.get("location"),
            "camera_id": attrs.get("camera_id"),
            "vehicle_count": attrs.get("vehicle_count"),
            "traffic_score": attrs.get("traffic_score"),
            "status": attrs.get("status"),
            "last_updated": attrs.get("last_updated")
        })
    return kamere


def ask_chatbot(user_question, kamere):
    system_prompt = f"""Ti si AI asistent za saobraćaj u Beogradu. 
Odgovaraš na srpskom jeziku, kratko i jasno.
Nikada ne izmišljaš podatke — koristiš samo podatke koje dobijaš.
VAŽNA PRAVILA:
- Ne spominješ traffic_score nikada
- Broj vozila spominješ SAMO ako korisnik direktno pita "koliko vozila", "koliko automobila", "koliko kola" ili slično
- Ako korisnik već pomene lokaciju u pitanju, ne ponavljaj je u odgovoru
- Odgovori jednom rečenicom
- Nikada ne izmišljaš podatke

Koristi SAMO ove opise stanja:
- protočno → biraš između: "nema gužve", "samo par auta"
- usporeno → biraš između: "ima gužve ali je prohodno", "malo je sporije ali prolazi", "usporen saobraćaj ali se kreće"
- velika gužva → biraš između: "ima gužve, sve stoji", "stoji, ne kreće se", "velika gužva, teško je proći"
- na pitanja koliko auta vidiš treba da odgovoriš samo za lokaciju koja je prethodno postavljena, odnosno na koju se konverzacija odnosi

Trenutno stanje saobraćaja (poslednja analiza):
{kamere}

Primeri DOBROG odgovora:
- Korisnik pita "ima li gužve na Brankovom mostu?" → "Nema gužve, samo par auta."
- Korisnik pita "šta je sa Kraljem Milanom?" → "Malo je sporije ali prolazi."
- Korisnik pita "koliko vozila ima na Brankovom mostu?" → "Trenutno vidim 12 vozila."
- Korisnik pita "kako je saobraćaj?" → "Na Brankovom mostu nema gužve, a na Kralja Milana ima gužve ali je prohodno."
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content


def run():
    print("🚦 TrafficLens AI — Chatbot")
    print("Pitajte o saobraćaju u Beogradu (maksimalno 3 pitanja)")
    print("-" * 40)

    broj_pitanja = 0
    MAX_PITANJA = 3

    while broj_pitanja < MAX_PITANJA:
        preostalo = MAX_PITANJA - broj_pitanja
        user_input = input(f"\nVi ({preostalo} pitanja preostalo): ").strip()

        if user_input.lower() in ["kraj", "exit", "quit"]:
            print("Doviđenja!")
            break
        if not user_input:
            continue

        kamere = get_traffic_data()
        odgovor = ask_chatbot(user_input, kamere)
        print(f"\nTrafficLens: {odgovor}")

        broj_pitanja += 1

    if broj_pitanja >= MAX_PITANJA:
        print("\n⚠️ Iskoristili ste sva 3 pitanja. Hvala što ste koristili TrafficLens AI!")


if __name__ == "__main__":
    run()