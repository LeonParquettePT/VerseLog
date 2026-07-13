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
- Epic 6 (Installeur graphique) : **in-progress**. Nouvel epic, package Python `verselog_installer` séparé de `verselog` (aucune dépendance inverse).
  - Story 6.1 (coquille de l'assistant + étape benchmark) : **done**. Étapes Welcome + Benchmark fonctionnelles, réutilise `Benchmark`/`SettingsStore` de l'app principale. Packaging PyInstaller de `verselog-installer.exe` volontairement reporté à la fin de l'epic (Story 6.3).
  - Story 6.2 (sélection des composants + installation guidée) : **done**. Cases à cocher pré-remplies selon le tier de benchmark recommandé, bouton "Install Selected" qui ouvre les installeurs/téléchargements officiels (jamais d'install silencieuse scriptée).
  - Story 6.3 (écran de fin + raccourci) : **done**. Écran de fin avec message de complétion + deux cases à cocher (raccourci Bureau / Menu Démarrer), création réelle du `.lnk` via PowerShell/`WScript.Shell` (pas de nouvelle dépendance pip). Revue de code a trouvé et corrigé 2 bugs réels : absence de gestion d'erreur (un PowerShell bloqué par une stratégie de groupe laissait l'assistant bloqué sans retour au joueur) et un risque d'injection/corruption via l'interpolation non échappée des chemins dans la commande PowerShell (corrigé avec des chaînes PowerShell à guillemets simples). L'installeur guidé (Stories 6.1-6.3) est maintenant fonctionnellement complet — reste le packaging PyInstaller de `verselog-installer.exe` lui-même, volontairement pas encore fait.
  - Story 6.4 (fixer la flakiness Tk() des tests, projet entier) : **backlog**, amélioration d'infra de test, pas bloquante — c'est la seule story qui garde Epic 6 en `in-progress` plutôt que `done`.
- Pages de revue de projet (`docs/project-review.html`/`-fr.html`) mises à jour le 2026-07-13 pour couvrir Epics 4, 5 et 6 (étaient restées figées à "3 epics" depuis avant le début de cette session) — plus polish UX (scrollbar, section active en surbrillance, retour à la doc).

## Découvertes/limitations connues (non bloquantes)

- **Windows Smart App Control** peut bloquer `verselog.exe` (non signé) — pas de bouton "exécuter quand même", il faut le désactiver temporairement dans Sécurité Windows. Documenté dans les notes de Release et le README.
- **Tier vision (Ollama) gourmand en RAM** une fois réellement utilisé pour l'inférence — confirmé : fonctionne sur une VM à 4 Go tant que le modèle n'est pas chargé, plus du tout une fois utilisé. D'où Story 5.7.
- **Release Windows obsolète** (voir Story 5.1 ci-dessus) — à reconstruire avant toute nouvelle communication publique du lien de téléchargement Windows.
- **Flakiness d'environnement connue (non liée au code) :** créer beaucoup de fenêtres `tk.Tk()` réelles dans une même exécution de la suite de tests complète déclenche parfois une `TclError` transitoire à la construction — confirmé que ça touche plusieurs fichiers de tests pré-existants sans rapport entre eux (jamais le même deux fois de suite), pas un bug de code. Se résout en relançant les tests. Fix propre suivi en Story 6.4.

## Prochaine étape suggérée

Trois pistes possibles, aucune priorité imposée : (1) reconstruire/republier la release Windows pour inclure Stories 5.3/5.5/5.6, (2) packager `verselog-installer.exe` avec PyInstaller (l'installeur guidé lui-même est maintenant fonctionnellement complet), ou (3) stories backlog restantes : 5.4, 5.7, 6.4.

## Où retrouver le contexte complet

- Documentation publiée : https://leonparquettept.github.io/VerseLog/
- Toutes les stories (détail complet de ce qui a été fait, comment, et pourquoi) : `_bmad-output/implementation-artifacts/*.md`
- État de toutes les stories (source de vérité) : `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Toutes les epics/stories, y compris le backlog : `_bmad-output/planning-artifacts/epics.md`
- Architecture : `_bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md`
- Contrat/spec du projet : `_bmad-output/specs/spec-verselog/SPEC.md`
