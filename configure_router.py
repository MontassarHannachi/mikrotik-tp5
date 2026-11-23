
import os
import json
import requests
import urllib3
from dotenv import load_dotenv

# Charger les identifiants depuis .env
load_dotenv()

HOST = os.getenv("DEVICE_HOST")
USER = os.getenv("DEVICE_USER")
PASSWORD = os.getenv("DEVICE_PASSWORD")

if not all([HOST, USER, PASSWORD]):
    raise SystemExit("Erreur : vérifie le fichier .env")

BASE_URL = f"https://{HOST}/rest"
AUTH = (USER, PASSWORD)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.auth = AUTH
session.verify = False

# Routes à configurer : destination et passerelle
routes = [
    {
        "destination": "172.20.0.0/16",
        "gateway": "10.0.2.2"
    }
]

def api_request(method, endpoint, **kwargs):
    response = session.request(
        method,
        f"{BASE_URL}{endpoint}",
        timeout=10,
        **kwargs
    )
    response.raise_for_status()

    if response.content:
        return response.json()

    return None


try:
    # Lire les routes existantes
    print("--- GET : lecture des routes existantes ---")
    existing_routes = api_request("GET", "/ip/route")
    print(json.dumps(existing_routes, indent=4))

    for route in routes:
        destination = route["destination"]
        gateway = route["gateway"]

        # Vérifier si la destination existe déjà
        existing = next(
            (
                item for item in existing_routes
                if item.get("dst-address") == destination
            ),
            None
        )

        if existing:
            if existing.get("gateway") == gateway:
                print(
                    f"Route déjà présente : {destination} "
                    f"via {gateway}. Aucune création."
                )
                continue

            raise RuntimeError(
                f"Conflit : {destination} existe déjà "
                f"avec une autre passerelle : {existing.get('gateway')}"
            )

        # Créer uniquement une route manquante
        print(f"\nCréation de {destination} via {gateway}...")

        created = api_request(
            "PUT",
            "/ip/route",
            json={
                "dst-address": destination,
                "gateway": gateway,
                "comment": "TP5-Python-idempotence"
            }
        )

        print("Route créée :", created)

        # Actualiser la liste après création
        existing_routes = api_request("GET", "/ip/route")

        verified = any(
            item.get("dst-address") == destination
            and item.get("gateway") == gateway
            for item in existing_routes
        )

        if not verified:
            raise RuntimeError(
                f"Vérification échouée pour {destination}"
            )

        print("Route vérifiée avec succès.")

    print("\nConfiguration terminée.")

except requests.exceptions.HTTPError as error:
    print("\nErreur HTTP :", error)
    if error.response is not None:
        print("Détail :", error.response.text)

except (requests.exceptions.RequestException, RuntimeError) as error:
    print("\nErreur :", error)

finally:
    session.close()
