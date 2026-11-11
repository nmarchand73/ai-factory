# Origine

Cette factory est un fork assumé de la *software factory v2* de ZazenCodes
(<https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2>),
publiée sous GPLv3 (voir `LICENSE`). Elle évolue ici de façon indépendante : aucune
synchronisation avec l'amont n'est prévue.

Principales différences :

- la factory vit dans son propre repo et travaille sur **plusieurs projets cibles** depuis l'extérieur
  (clone local + worktrees), au lieu d'être copiée dans chaque projet ;
- `config.json` déclare les cibles ; `checks.sh` et `notes.md` sont par cible ;
- `factory/bin/target` ajoute et vérifie une cible ;
- le dashboard affiche un swimlane par projet ;
- tous les appels `gh` nomment leur repo (`--repo`), aucun ne dépend du dossier courant.
