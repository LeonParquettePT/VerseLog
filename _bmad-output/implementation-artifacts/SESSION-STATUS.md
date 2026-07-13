# VerseLog — Point d'étape (mis à jour à chaque session)

Ce fichier est la source de vérité pour reprendre le projet rapidement, avec Claude ou une autre IA, sans tout réexpliquer. Il est mis à jour à chaque changement notable et poussé sur `origin/main` — toujours à jour sur GitHub même si la machine locale a un problème.

Lien direct (toujours valable, même nom de fichier) :
https://github.com/LeonParquettePT/VerseLog/blob/main/_bmad-output/implementation-artifacts/SESSION-STATUS.md

## État du projet (2026-07-13)

- Epics 1 à 4 : **done** (toutes les stories).
- Epic 5 (Packaging & Distribution) : **in-progress**.
  - Story 5.1 (Windows/PyInstaller) : **done**. Release GitHub `v0.1.0-windows` — **note : cette release date d'avant les Stories 5.3/5.5/5.6, elle est obsolète et doit être reconstruite** avant de la donner à un joueur.
  - Story 5.2 (Linux packaging via GitHub Actions) : **done**. Release GitHub `v0.1.0-linux`. Vérifié de bout en bout sur une vraie VM Ubuntu Desktop (fenêtre Tkinter comprise).
  - Story 5.3 (détection Tesseract/Ollama/modèle de vision manquants) : **done**.
  - Story 5.5 (sélection du vaisseau via l'UI) : **done**.
  - Story 5.6 (sélection de l'écran de capture) : **done**. Nouveau flag `--monitor`.
  - Story 5.4 (signature de code, SignPath Foundation) : **backlog**, volontaire.
  - Story 5.7 (benchmark sensible à la RAM disponible) : **backlog**.
- **Nouvel epic proposé (pas encore créé formellement) : installeur graphique Windows** — assistant multi-étapes séparé (`verselog-installer.exe`, Tkinter), benchmark d'abord, puis sélection des composants à installer (cases à cocher), recommandation pré-remplie selon le benchmark, écran de fin avec proposition de raccourci. Idée du propriétaire du projet (2026-07-13), approche technique validée mais pas encore démarrée.

## Découvertes/limitations connues (non bloquantes)

- **Windows Smart App Control** peut bloquer `verselog.exe` (non signé) — pas de bouton "exécuter quand même", il faut le désactiver temporairement dans Sécurité Windows. Documenté dans les notes de Release et le README.
- **Tier vision (Ollama) gourmand en RAM** une fois réellement utilisé pour l'inférence — confirmé : fonctionne sur une VM à 4 Go tant que le modèle n'est pas chargé, plus du tout une fois utilisé. D'où Story 5.7.
- **Release Windows obsolète** (voir Story 5.1 ci-dessus) — à reconstruire avant toute nouvelle communication publique du lien de téléchargement Windows.

## Prochaine étape suggérée

Deux pistes possibles, aucune priorité imposée : (1) reconstruire/republier la release Windows pour inclure Stories 5.3/5.5/5.6, ou (2) démarrer le nouvel epic "installeur graphique" décrit ci-dessus. Sinon, stories backlog restantes : 5.4, 5.7.

## Où retrouver le contexte complet

- Documentation publiée : https://leonparquettept.github.io/VerseLog/
- Toutes les stories (détail complet de ce qui a été fait, comment, et pourquoi) : `_bmad-output/implementation-artifacts/*.md`
- État de toutes les stories (source de vérité) : `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Toutes les epics/stories, y compris le backlog : `_bmad-output/planning-artifacts/epics.md`
- Architecture : `_bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md`
- Contrat/spec du projet : `_bmad-output/specs/spec-verselog/SPEC.md`
