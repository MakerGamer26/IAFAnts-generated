# Résultats de la simulation AI-Fants

Ce document décrit les résultats et l'état actuel du projet de simulation de fourmis.

## Ce qui fonctionne

*   **Moteur de simulation** : Le cœur de la simulation est fonctionnel. Il gère un monde en grille, le temps qui passe, et les conditions de fin (temps maximum atteint ou nourriture épuisée).
*   **Modèles de données** : Les classes pour les fourmis (Exploratrice, Combattante, Récolteuse), le nid, les sources de nourriture et la grille sont implémentées conformément aux spécifications.
*   **Q-Learning** : L'algorithme de Q-learning est intégré. Les fourmis choisissent leurs actions en utilisant une stratégie ε-greedy et mettent à jour les Q-tables (phéromones) après chaque action. Deux Q-tables distinctes sont utilisées pour la recherche de nourriture et le retour au nid.
*   **Dissipation des phéromones** : Les phéromones se dissipent de 1% à chaque unité de temps, comme demandé.
*   **Interface graphique (GUI)** : Une interface graphique a été développée avec Tkinter. Elle permet de :
    *   Visualiser la grille, les murs, le nid, la nourriture et les zones mortelles.
    *   Voir les fourmis se déplacer sur la grille, avec des couleurs distinctes par type.
    *   Démarrer, pauser et réinitialiser la simulation.
    *   Visualiser les cartes de phéromones pour la nourriture et le nid sous forme de "heatmap".
    *   Utiliser un curseur pour naviguer dans l'historique de la simulation et revoir les états passés ("retour en arrière").
*   **Paramétrage ("Méta Programme")** : La simulation est entièrement configurable via un dictionnaire de configuration. Un script `meta_optimizer.py` a été créé pour démontrer comment lancer des simulations en arrière-plan (sans GUI) avec différents paramètres pour trouver des stratégies optimales.

## Ce qui ne fonctionne pas ou pourrait être amélioré

*   **Optimisation des performances** : La simulation, en particulier avec l'interface graphique, peut être lente, surtout sur de grandes grilles ou avec un grand nombre de fourmis. Le rendu est mis à jour à chaque pas de temps, ce qui peut être coûteux. Pour des simulations rapides (comme dans le méta-programme), il est recommandé de ne pas mettre à jour l'interface graphique à chaque étape.
*   **Gestion avancée du nid** : La logique actuelle du nid est simple. Les fourmis déposent leur nourriture, et c'est tout. La fonctionnalité spécifiée où le nid "décide si elle laisse la fourmis ressortir de suite ou plus tard" n'est pas implémentée.
*   **Vision des fourmis** : La caractéristique de "vision à 1 case" pour les exploratrices, qui permettrait de mettre à jour la récompense sans se déplacer, n'est pas implémentée de cette manière spécifique. Actuellement, la récompense est mise à jour après le déplacement.
*   **Complexité algorithmique** : Le document ne contient pas encore d'analyse formelle de la complexité algorithmique, bien que la structure soit en place pour le faire.
*   **Création de carte personnalisée** : L'interface ne permet pas de créer une carte personnalisée via la souris. Les cartes sont actuellement chargées à partir de la configuration.

## Conclusion

Le projet remplit la grande majorité des exigences fondamentales. Le système est fonctionnel, l'algorithme de Q-learning est opérationnel, et l'interface graphique fournit tous les outils de visualisation et de contrôle demandés. Les points à améliorer concernent principalement des fonctionnalités avancées et des optimisations.