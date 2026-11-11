# AI Factory (hub)

Ce repo contient la factory, pas le code des projets : ils sont déclarés dans `factory/config.json`
(`targets`) et clonés dans `targets/<nom>/repo`. Les agents et le skill (`.claude/`) sont communs à toutes les cibles.

## Règles
- `factory/bin/job` est le seul écrivain de `factory/jobs/<id>/job.json` ; ne l'éditez pas à la main.
- Chaque appel `gh` du code nomme son repo (`--repo`) ; n'en ajoutez pas qui dépendent du dossier courant.
- Ne modifiez jamais `targets/*/repo` ni `workspaces/` à la main : seuls les scripts y touchent.
- Les checks d'une cible sont dans `targets/<nom>/checks.sh` (non interactif, sans réécriture de fichiers).

## Validation
`python3 -m unittest tests/test_factory.py` (utilise un faux `gh` et des dépôts git locaux).

## Commandes
`/factory run [<cible>]`, `/factory run <cible>#<n>`, `/factory <texte libre>`.
Ajouter un projet : `factory/bin/target add <nom> <owner/repo>` puis `factory/bin/target check <nom>`.
