# Trame de présentation orale

## 1. Introduction (30 secondes)

« Notre application de bureau a été développée avec Tkinter. Elle couvre deux axes : la collecte de données JSON avec stockage SQLite et l'analyse d'un livre Project Gutenberg avec génération automatique d'un rapport Word. »

## 2. Démonstration conseillée (3 à 4 minutes)

1. Lancer `app.py` et montrer les trois onglets.
2. Cliquer sur **Télécharger JSON**.
3. Relancer le téléchargement pour montrer le choix remplacer/ajouter/annuler quand la base n'est pas vide.
4. Cliquer sur **Agrégation SQL**, puis afficher le graphique dans l'onglet dédié.
5. Modifier le thème et la taille de police depuis le menu **Options**.
6. Lancer **Télécharger et analyser le livre** et présenter les statistiques.
7. Montrer le graphique des longueurs de paragraphes intégré à la fenêtre.
8. Exporter le rapport Word et ouvrir le fichier généré.
9. Montrer le logo pivoté sur la couverture et les deux pages du rapport.
10. Terminer avec l'exécution des tests unitaires.

## 3. Questions probables

### Pourquoi SQLite ?
SQLite ne nécessite pas de serveur, reste simple à distribuer et prend en charge les requêtes d'agrégation demandées.

### Que se passe-t-il si la base n'est pas vide ?
Une boîte de dialogue propose de remplacer les données, d'ajouter uniquement les nouveaux enregistrements ou d'annuler.

### Pourquoi utiliser des threads ?
Les téléchargements et la création du rapport peuvent prendre du temps. Les threads évitent de figer l'interface Tkinter.

### Comment les exceptions sont-elles gérées ?
Les erreurs réseau, JSON, image, analyse du livre et génération Word sont interceptées et affichées dans une boîte de dialogue sans fermer l'application.

### Comment la dizaine est-elle calculée ?
La consigne indique que 123, 127 et 129 deviennent 120. Le programme utilise donc une division entière par 10 suivie d'une multiplication par 10.

### Quels tests ont été réalisés ?
Les tests vérifient la base SQLite, les doublons, les agrégations, l'extraction des métadonnées et du chapitre, le comptage de mots et la distribution.

## 4. Commandes de démonstration

```bash
python -m pip install -r requirements.txt
python app.py
python -m unittest discover -s tests -v
```
