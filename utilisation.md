# Guide d'utilisation de AI-Fants

Ce document explique comment lancer et utiliser le programme de simulation de fourmis.

## Prérequis

*   Python 3.x
*   Tkinter (généralement inclus avec les installations standard de Python)

Aucune bibliothèque externe n'est requise.

## Comment lancer la simulation avec l'interface graphique

Pour lancer la simulation avec l'interface visuelle, exécutez la commande suivante à la racine du projet :

```bash
python3 main.py
```

Cela ouvrira une fenêtre affichant la simulation.

### Contrôles de l'interface

*   **Start** : Démarre ou reprend la simulation.
*   **Pause** : Met la simulation en pause.
*   **Reset** : Réinitialise la simulation à son état initial.
*   **Curseur de temps (Slider)** : Lorsque la simulation est en pause, vous pouvez faire glisser ce curseur pour "remonter dans le temps" et visualiser l'état de la simulation à n'importe quel moment passé.
*   **Boutons radio "Pheromone View"** :
    *   **None** : Vue par défaut, sans phéromones.
    *   **Food** : Affiche une "heatmap" (carte de chaleur) des phéromones menant à la nourriture. Les zones plus rouges indiquent une plus forte concentration de phéromones.
    *   **Nest** : Affiche une "heatmap" des phéromones menant au nid. Les zones plus bleues indiquent une plus forte concentration.

## Comment lancer des simulations en arrière-plan (Méta Programme)

Pour les tests de performance ou l'optimisation des paramètres, vous pouvez exécuter des simulations sans l'interface graphique. Le script `meta_optimizer.py` est conçu pour cela.

Exécutez la commande suivante :

```bash
python3 meta_optimizer.py
```

Ce script va :
1.  Lancer une seule simulation avec les paramètres par défaut et afficher le temps de simulation final.
2.  Exécuter une boucle d'exemple qui teste différentes valeurs pour le paramètre `epsilon` du Q-learning, et indiquer quelle valeur a permis de terminer la simulation le plus rapidement.

## Comment personnaliser la simulation

Tous les paramètres de la simulation peuvent être modifiés dans le dictionnaire `DEFAULT_CONFIG` situé au début du fichier `main.py`.

Vous pouvez modifier :
*   La taille de la grille (`grid_width`, `grid_height`).
*   La carte (`map`) en utilisant des caractères pour représenter les différents éléments :
    *   `'N'` : Nid
    *   `'W'` : Mur
    *   `'F'` : Nourriture
    *   `'D'` : Zone mortelle
    *   `'.'` : Case vide
*   La quantité de nourriture sur chaque case (`food_quantities`).
*   Le nombre et le type de fourmis dans le nid (`nest`).
*   Les paramètres de l'algorithme Q-learning (`q_learning`).
*   Les récompenses et le taux de dissipation des phéromones (`pheromones`).