from typing import Any

import requests

from config import JSON_API_URL, NETWORK_TIMEOUT, USER_AGENT
from models import TodoRecord


class ApiError(RuntimeError):
    pass


FRENCH_TASKS = (
    "Préparer le rapport hebdomadaire",
    "Vérifier les données du projet",
    "Mettre à jour la liste des utilisateurs",
    "Organiser la documentation technique",
    "Finaliser les paramètres de sécurité",
    "Contrôler le calendrier de l'équipe",
    "Planifier la prochaine sauvegarde",
    "Corriger le tableau de suivi",
    "Analyser les résultats enregistrés",
    "Envoyer le compte rendu",
    "Archiver les anciens fichiers",
    "Réviser la présentation du projet",
    "Configurer la base de données",
    "Tester les nouvelles fonctionnalités",
    "Nettoyer les données inutiles",
    "Synchroniser les fichiers locaux",
    "Valider les modifications récentes",
    "Créer une copie de sauvegarde",
    "Optimiser le temps de traitement",
    "Documenter les erreurs détectées",
)

FRENCH_CONTEXTS = (
    "pour l'équipe",
    "avant la prochaine réunion",
    "pour la présentation finale",
    "avec les dernières informations",
    "selon les consignes du projet",
    "pour le responsable du groupe",
    "avant la sauvegarde générale",
    "pour le suivi mensuel",
    "avec les paramètres actuels",
    "avant la validation définitive",
)


def build_french_task_name(remote_id: int) -> str:
    """Crée un intitulé français stable à partir de l'identifiant reçu par l'API."""
    index = max(remote_id - 1, 0)
    task = FRENCH_TASKS[index % len(FRENCH_TASKS)]
    context = FRENCH_CONTEXTS[(index // len(FRENCH_TASKS)) % len(FRENCH_CONTEXTS)]
    return f"{task} {context}"


def download_todos(url: str = JSON_API_URL) -> list[TodoRecord]:
    try:
        response = requests.get(
            url,
            timeout=NETWORK_TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        response.raise_for_status()
        payload: Any = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ApiError(f"Impossible de télécharger les données JSON : {exc}") from exc

    if not isinstance(payload, list):
        raise ApiError("Format JSON inattendu : une liste était attendue.")

    records: list[TodoRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        try:
            remote_id = int(item["id"])
            completed = bool(item["completed"])
            french_name = build_french_task_name(remote_id)
            records.append(
                TodoRecord(
                    remote_id=remote_id,
                    user_id=int(item["userId"]),
                    name=french_name,
                    state="Terminé" if completed else "En attente",
                    length=len(french_name),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue

    if not records:
        raise ApiError("Aucune donnée exploitable n'a été reçue.")
    return records
