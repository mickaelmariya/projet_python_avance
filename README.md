# Projet Python Avancé - application desktop

Application Tkinter complète répondant aux deux parties du sujet : téléchargement JSON, stockage SQLite, agrégation SQL, graphiques intégrés, analyse d'un livre Project Gutenberg, traitement d'images et export Word.

## Fonctionnalités

- Téléchargement des tâches JSON depuis JSONPlaceholder.
- Stockage d'un sous-ensemble dans SQLite : ID, utilisateur, nom, état et longueur.
- Si la base n'est pas vide, choix entre **remplacer**, **ajouter uniquement les nouveautés** ou **annuler**.
- Agrégation SQL : total, moyenne, minimum, maximum, terminés et en attente.
- Graphique Matplotlib affiché directement dans la fenêtre principale.
- Menu d'options pour les couleurs et la taille de police.
- Ligne d'état en bas de la fenêtre.
- Téléchargement et analyse de *Alice's Adventures in Wonderland*.
- Extraction du titre, de l'auteur et du premier chapitre.
- Comptage des mots par paragraphe et regroupement par dizaine inférieure : 123, 127 et 129 deviennent 120.
- Téléchargement d'une couverture, recadrage/redimensionnement, rotation et collage d'un logo noir et blanc local.
- Création d'un rapport Word avec page de titre, image, graphique, statistiques, sources et extrait.
- Téléchargements et traitements exécutés dans des threads pour ne pas bloquer l'interface.
- Gestion des exceptions et tests unitaires.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
python app.py
```

Sous Windows, vous pouvez aussi lancer `run.bat`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Structure

- `app.py` : interface Tkinter et orchestration.
- `database.py` : SQLite et requêtes SQL.
- `api_service.py` : téléchargement/validation JSON.
- `book_service.py` : livre, paragraphes, graphique et images.
- `report_service.py` : génération du document Word.
- `assets/logo_bw.png` : logo local noir et blanc.
- `data/application.db` : base créée automatiquement.
- `output/` : images, graphique et rapport Word.

## Langue des données JSON

L’API JSONPlaceholder fournit des intitulés de démonstration en pseudo-latin. L’application conserve les identifiants, les utilisateurs et les états reçus depuis Internet, puis produit des intitulés français stables pour l’affichage et le stockage SQLite. La source et cette adaptation sont indiquées directement dans l’interface.

## Mode secours Project Gutenberg

Project Gutenberg peut parfois répondre lentement ou être bloqué par un réseau d’école/entreprise. L’application essaie plusieurs adresses officielles avec un délai limité. Si elles échouent, elle utilise automatiquement une copie locale officielle du texte et de la couverture, placée dans `assets/`, afin que la démonstration et l’export Word continuent sans erreur.

Dans l’onglet **Livre et rapport Word**, la ligne **Source du texte** indique clairement :

- `Internet — ...` quand le téléchargement en ligne a fonctionné ;
- `Copie locale de secours Project Gutenberg` quand le site n’a pas répondu.

Le rapport Word conserve également cette information.
