# AI Factory

Une software factory pilotée par Claude Code : une issue GitHub étiquetée `factory` devient une pull request
(intake → spec → build → gate → relecteurs en parallèle → approver). La factory vit **ici** et travaille sur
autant de projets que vous voulez, qui ne reçoivent que des PR. Fork de la v2 de ZazenCodes, voir `docs/ORIGIN.md`.

## Démarrer

```bash
factory/bin/target add mon-projet owner/repo      # clone, labels, checks.sh et notes.md à compléter
$EDITOR targets/mon-projet/checks.sh targets/mon-projet/notes.md
factory/bin/target check mon-projet               # doit finir par « target is ready »
gh issue edit 12 --repo owner/repo --add-label factory
claude                                            # à la racine de CE repo
> /factory run mon-projet#12                      # ou /factory run
```

Dashboard (un swimlane par projet) : `cd factory && python3 -m http.server`, puis <http://localhost:8000/dashboard.html>.

Manuel complet : `docs/manuel-factory.html`. Tests : `python3 -m unittest tests/test_factory.py`.

## Organisation

```
.claude/skills/factory, .claude/agents   l'orchestrateur et les 8 agents (une seule copie)
factory/                                  config.json, bin/{job,gate,route,target}, dashboard.html
targets/<nom>/checks.sh, notes.md         checks et consignes propres à chaque projet (commités)
targets/<nom>/repo                        clone local du projet (gitignoré)
workspaces/<nom>/<job>                    worktrees des jobs (gitignoré)
factory/jobs/<job>                        état des jobs (gitignoré)
```
