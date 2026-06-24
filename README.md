# Projet Python Avancé — Data & Livre

Application de bureau développée en **Python avec Tkinter** dans le cadre du projet Python Avancé.

Elle permet de télécharger des données JSON depuis Internet, de les enregistrer dans une base SQLite, d'afficher des statistiques et des graphiques, puis d'analyser un livre de Project Gutenberg et de générer automatiquement un rapport Word.

## Fonctionnalités

### Données JSON et SQLite

- Téléchargement de données JSON depuis JSONPlaceholder.
- Adaptation des intitulés en français pour l'affichage.
- Enregistrement dans une base de données SQLite.
- Gestion d'une base déjà remplie :
  - remplacement des anciennes données ;
  - ajout des nouvelles données uniquement ;
  - annulation de l'opération.
- Affichage des données dans un tableau Tkinter.
- Suppression complète du contenu de la base.
- Calcul d'agrégations avec une requête SQL :
  - nombre total d'éléments ;
  - éléments terminés ;
  - éléments en attente ;
  - longueur moyenne ;
  - longueur minimale ;
  - longueur maximale.
- Affichage d'un graphique Matplotlib dans la fenêtre principale.

### Analyse d'un livre

- Téléchargement de *Alice's Adventures in Wonderland*.
- Extraction du titre, de l'auteur et du premier chapitre.
- Découpage du premier chapitre en paragraphes.
- Comptage du nombre de mots par paragraphe.
- Regroupement des longueurs par dizaines.
- Génération d'un graphique de distribution.
- Calcul des statistiques du chapitre :
  - nombre de paragraphes ;
  - nombre total de mots ;
  - minimum ;
  - maximum ;
  - moyenne.

### Images et rapport Word

- Téléchargement d'une image liée au livre.
- Recadrage et redimensionnement avec Pillow.
- Rotation d'un logo noir et blanc local.
- Insertion du logo dans l'image principale.
- Création automatique d'un document Word contenant :
  - une page de titre ;
  - le titre du livre ;
  - le nom de l'auteur ;
  - le nom de l'auteur du rapport ;
  - l'image modifiée ;
  - le graphique de distribution ;
  - les statistiques du premier chapitre ;
  - la source des données.

### Qualité et robustesse

- Interface entièrement en français.
- Gestion des exceptions afin d'éviter les blocages.
- Utilisation de threads pour garder l'interface réactive.
- Ligne d'état indiquant la dernière opération effectuée.
- Choix du thème clair ou sombre.
- Modification de la taille de la police.
- Mode de secours local si Project Gutenberg ne répond pas.
- 7 tests unitaires fonctionnels.

## Technologies utilisées

- Python 3
- Tkinter
- SQLite
- Requests
- Matplotlib
- Pillow
- python-docx
- unittest

## Installation

### 1. Cloner le dépôt

```bash
git clone URL_DU_DEPOT.git
cd projet_python_avance
```

Remplacez `URL_DU_DEPOT.git` par l'adresse de votre dépôt GitHub.

### 2. Créer un environnement virtuel

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

## Lancement

### Méthode rapide sous Windows

Double-cliquez sur :

```text
run.bat
```

### Depuis un terminal

```bash
python app.py
```

## Démonstration conseillée

1. Lancer l'application.
2. Cliquer sur **Vider la base**.
3. Cliquer sur **Télécharger JSON**.
4. Vérifier que le tableau contient 200 lignes.
5. Cliquer sur **Agrégation SQL**.
6. Ouvrir l'onglet **Graphique JSON** et afficher le graphique.
7. Ouvrir l'onglet **Livre et rapport Word**.
8. Lancer le téléchargement et l'analyse du livre.
9. Vérifier les statistiques et le graphique.
10. Exporter le rapport Word.
11. Ouvrir le document généré dans le dossier `output`.

## Tests unitaires

Exécuter tous les tests avec :

```bash
python -m unittest discover -s tests -v
```

Résultat attendu :

```text
Ran 7 tests
OK
```

## Structure du projet

```text
projet_python_avance/
├── app.py
├── api_service.py
├── book_service.py
├── config.py
├── database.py
├── models.py
├── report_service.py
├── requirements.txt
├── run.bat
├── README.md
├── PRESENTATION_ORALE.md
├── .gitignore
├── assets/
│   ├── logo_bw.png
│   ├── alice_backup.txt
│   └── alice_cover_backup.jpg
├── data/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── tests/
    ├── test_api_service.py
    ├── test_book_service.py
    └── test_database.py
```

## Mode de secours Project Gutenberg

Project Gutenberg peut parfois être lent ou inaccessible depuis certains réseaux.

L'application essaie plusieurs adresses officielles. En cas d'échec, elle utilise automatiquement :

```text
assets/alice_backup.txt
assets/alice_cover_backup.jpg
```

L'analyse du livre, le graphique et l'export Word continuent donc de fonctionner même sans réponse du site.

## Fichiers générés

Les résultats sont enregistrés dans le dossier :

```text
output/
```

Ce dossier peut contenir notamment :

```text
paragraph_distribution.png
alice_processed.jpg
rapport_alice.docx
```

La base SQLite est créée automatiquement dans :

```text
data/application.db
```

## Publication sur GitHub

Après avoir créé un dépôt vide sur GitHub, exécutez dans le dossier du projet :

```bash
git init
git add .
git commit -m "Ajout du projet Python Avancé"
git branch -M main
git remote add origin URL_DU_DEPOT.git
git push -u origin main
```

## Auteur

**Mariyanayagam Mickaël**  
Étudiant à Ynov Campus Paris
