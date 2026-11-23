# TP 5 — MikroTik CHR v7 : API RESTful

## 1. Présentation

Ce TP a pour objectif de découvrir et d'utiliser l'API REST de MikroTik RouterOS v7 afin d'automatiser certaines opérations d'administration réseau avec Python.

## 2. Environnement utilisé

- Système hôte : Windows 11
- Hyperviseur : VirtualBox
- Routeur : MikroTik CHR v7
- Langage : Python 3
- Bibliothèques : requests et python-dotenv
- Protocole : HTTPS / API REST

### Configuration réseau

| Élément | Configuration |
|---|---|
| Interface ether1 | NAT, adresse DHCP |
| Interface ether2 | Réseau Host-only |
| Adresse du routeur sur ether2 | 192.168.56.10/24 |
| Adresse de l'hôte Windows | 192.168.56.1/24 |
| Port HTTPS | 443 |

## 3. Structure du projet

```text
mikrotik-tp5/
├── .env
├── .gitignore
├── crud_mikrotik.py
├── configure_router.py
└── README.md
```

Le fichier `.env` contient les paramètres de connexion. Il est volontairement exclu du dépôt Git.

## 4. Installation

Installer les bibliothèques Python :

```powershell
py -m pip install requests python-dotenv
```

Créer le fichier `.env` à la racine du projet avec les paramètres suivants :

```env
DEVICE_HOST=192.168.56.10
DEVICE_USER=api-user
DEVICE_PASSWORD=VOTRE_MOT_DE_PASSE
```

Remplacer `VOTRE_MOT_DE_PASSE` par le mot de passe configuré sur le routeur.

**Ne jamais publier le fichier `.env` ni son contenu.**

## 5. Script CRUD : crud_mikrotik.py

Ce script automatise la gestion des adresses IP avec l'API REST.

Opérations réalisées :

1. GET : récupération des adresses IP existantes.
2. PUT : création d'une adresse IP de test.
3. GET : récupération de l'identifiant de l'adresse créée.
4. PATCH : modification du commentaire de l'adresse.
5. DELETE : suppression de l'adresse de test.
6. GET : vérification de la suppression.

Remarque : la création utilise PUT, conformément au fonctionnement de l'API REST RouterOS utilisé pendant ce TP.

Exécution :

```powershell
py crud_mikrotik.py
```

## 6. Script d'automatisation : configure_router.py

Ce script automatise l'ajout d'une route statique.

Route de démonstration :

- Destination : 172.20.0.0/16
- Passerelle : 10.0.2.2

Le script vérifie d'abord si la route existe :

- Si elle n'existe pas, il la crée.
- Si elle existe avec la même passerelle, il ne fait rien.
- Si elle existe avec une passerelle différente, il signale un conflit.

Cette logique permet de démontrer l'idempotence : plusieurs exécutions ne créent pas de routes en double.

Exécution :

```powershell
py configure_router.py
```

La route est utilisée comme exemple d'automatisation. Sa présence ne prouve pas que le réseau distant 172.20.0.0/16 est réellement accessible.

## 7. Sécurité

- Les identifiants sont stockés dans `.env`.
- `.env` est exclu du versionnement avec `.gitignore`.
- L'accès à l'API REST utilise HTTPS.
- Le certificat utilisé dans ce laboratoire est auto-signé.
- La vérification TLS désactivée dans les scripts est uniquement tolérée pour cet environnement de test local. En production, il faut utiliser un certificat de confiance et activer sa vérification.

## 8. Résultats obtenus

Les tests ont permis de vérifier :

- La connexion HTTPS au routeur MikroTik.
- La récupération des adresses IP avec GET.
- La création, la modification et la suppression d'une adresse IP.
- L'ajout d'une route statique.
- Le comportement idempotent du script d'automatisation.

## 9. Auteur

TP réalisé dans le cadre du module de programmation réseau.
