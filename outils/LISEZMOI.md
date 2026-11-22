# Générateur de séries problème/solution

`generateur_series.py` fabrique des séries de 5 images 1080x1350 (format Facebook 4:5) au style « plan bleu » : fond gris béton, titres bleu marine, accents orange.

Utilisation :
1. Remplacer le contenu du dictionnaire `SERIES` par les nouvelles séries (une clé par série, 5 diapos : PROBLÈME, CAUSE ou MÉCANISME, RISQUE ou ERREURS, SOLUTION, À RETENIR). Les séries `cure`, `fers` et `humidite` servent d'exemples.
2. `OUT=/chemin/sortie python3 outils/generateur_series.py` (Playwright + Chrome dans /usr/bin/google-chrome).
3. Copier les images dans un dossier par série à la racine du dépôt, puis pousser. Lien public : `https://raw.githubusercontent.com/wilfriednikiema58-collab/visuel-public-/main/<serie>/<serie>_<n>.jpg`.
