
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
    raise SystemExit("Erreur : vérifie les variables dans le fichier .env")

BASE_URL = f"https://{HOST}/rest"
AUTH = (USER, PASSWORD)

# Certificat auto-signé : acceptable pour ce laboratoire uniquement
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.auth = AUTH
session.verify = False

def request(method, endpoint, **kwargs):
    url = f"{BASE_URL}{endpoint}"
    response = session.request(method, url, timeout=10, **kwargs)
    response.raise_for_status()
    if response.content:
        return response.json()
    return None

try:
    # 1. GET : lire les adresses IP
    print("\n--- GET : adresses IP existantes ---")
    addresses = request("GET", "/ip/address")
    print(json.dumps(addresses, indent=4))

    # 2. POST : créer une adresse IP de test
    test_address = "192.168.20.1/24"
    print("\n--- PUT : création de l'adresse de test ---")

    existing = next(
        (item for item in addresses if item.get("address") == test_address
         and item.get("interface") == "ether2"),
        None
    )

    if existing:
        raise SystemExit(
            "L'adresse de test existe déjà. "
            "Ne pas la recréer : vérifie-la manuellement avant de continuer."
        )

    created = request(
        "PUT",
        "/ip/address",
        json={
            "address": test_address,
            "interface": "ether2",
            "comment": "TP5-Python-test"
        }
    )
    print("Adresse créée :", created)

    # 3. GET : retrouver l'adresse créée et son identifiant
    print("\n--- GET : recherche de l'adresse créée ---")
    addresses = request("GET", "/ip/address")

    target = next(
        (item for item in addresses
         if item.get("address") == test_address
         and item.get("interface") == "ether2"),
        None
    )

    if not target:
        raise RuntimeError("Adresse créée introuvable après le PUT.")

    address_id = target[".id"]
    print("Identifiant RouterOS :", address_id)

    # 4. PATCH : modifier le commentaire
    print("\n--- PATCH : modification du commentaire ---")
    request(
        "PATCH",
        f"/ip/address/{address_id}",
        json={"comment": "TP5-Python-modifie"}
    )

    addresses = request("GET", "/ip/address")
    target = next(
        (item for item in addresses if item.get(".id") == address_id),
        None
    )

    if not target or target.get("comment") != "TP5-Python-modifie":
        raise RuntimeError("La vérification du PATCH a échoué.")

    print("Commentaire modifié :", target.get("comment"))

    # 5. DELETE : supprimer l'adresse de test
    print("\n--- DELETE : suppression de l'adresse de test ---")
    request("DELETE", f"/ip/address/{address_id}")

    addresses = request("GET", "/ip/address")
    still_exists = any(
        item.get(".id") == address_id for item in addresses
    )

    if still_exists:
        raise RuntimeError("L'adresse existe encore après le DELETE.")

    print("Adresse de test supprimée et suppression vérifiée.")

    print("\nSUCCÈS : GET, PUT, PATCH et DELETE réalisés.")

except requests.exceptions.HTTPError as error:
    print("\nErreur HTTP :", error)
    if error.response is not None:
        print("Détail :", error.response.text)

except requests.exceptions.RequestException as error:
    print("\nErreur de connexion :", error)

except (KeyError, RuntimeError) as error:
    print("\nErreur :", error)

finally:
    session.close()
