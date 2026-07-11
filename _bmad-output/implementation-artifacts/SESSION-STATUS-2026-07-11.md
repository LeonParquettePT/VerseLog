# Point d'étape — 2026-07-11 (coupure imprévue, orage)

Tout le travail de code et de documentation est **committé et poussé sur `origin/main`** (dernier commit : `1ffdd2d`). Rien n'est perdu même si la machine coupe.

## État du projet
- Epics 1 à 4 : **done** (toutes les stories).
- Epic 5 (Packaging & Distribution) : **in-progress**.
  - Story 5.1 (Windows/PyInstaller) : **done**. Release GitHub `v0.1.0-windows` publiée avec `verselog.exe`.
  - Story 5.2 (Linux packaging) : **backlog** — prochaine priorité choisie par l'utilisateur.
  - Story 5.3 (vérif Tesseract/Ollama) : **backlog**.
  - Story 5.4 (signature de code, SignPath Foundation) : **backlog**, volontairement après 5.2.

## Découverte récente non résolue côté utilisateur
- `verselog.exe` est bloqué par le **Contrôle intelligent des applications (Smart App Control)** de Windows chez l'utilisateur — pas de bouton "exécuter quand même", il faut désactiver SAC temporairement (Sécurité Windows → Contrôle des applications et du navigateur), et il se re-bloquera probablement au lancement suivant si SAC est réactivé (fichier non signé). L'utilisateur n'arrive pas à modifier ce paramètre (l'interface se fige) — pistes données : vérifier Windows Update, vérifier "données de diagnostic facultatives" activées, vérifier si l'appareil est géré par une organisation. Pas urgent : pas bloquant pour la suite du projet, la vraie solution est Story 5.4 plus tard.

## Prochaine étape prévue
Reprendre avec **Story 5.2 (Linux packaging)** via un environnement jetable (GitHub Actions Linux runner), après l'échec de WSL en local. Utiliser le workflow BMad habituel : branche dédiée → `bmad-create-story` → `bmad-dev-story` → code-review → merge → marquer done.

## Où retrouver le contexte complet
- Documentation publiée : https://leonparquettept.github.io/VerseLog/
- Toutes les stories : `_bmad-output/implementation-artifacts/*.md`
- Sprint status : `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics : `_bmad-output/planning-artifacts/epics.md`
