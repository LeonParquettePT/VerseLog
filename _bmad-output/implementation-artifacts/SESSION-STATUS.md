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
  - Story 5.8 (recherche filtrante pour la sélection du vaisseau) : **backlog**. Léon a remarqué que la liste déroulante de la Story 5.5 (`ttk.Combobox` en lecture seule) n'a pas de filtre en direct — avec 100+ vaisseaux, taper pour filtrer serait plus pratique. Pas un bug (la liste actuelle empêche déjà toute faute de frappe), juste une amélioration UX confirmée souhaitée.
- Epic 6 (Installeur graphique) : **in-progress**. Nouvel epic, package Python `verselog_installer` séparé de `verselog` (aucune dépendance inverse).
  - Story 6.1 (coquille de l'assistant + étape benchmark) : **done**. Étapes Welcome + Benchmark fonctionnelles, réutilise `Benchmark`/`SettingsStore` de l'app principale. Packaging PyInstaller de `verselog-installer.exe` volontairement reporté à la fin de l'epic (Story 6.3).
  - Story 6.2 (sélection des composants + installation guidée) : **done**. Cases à cocher pré-remplies selon le tier de benchmark recommandé, bouton "Install Selected" qui ouvre les installeurs/téléchargements officiels (jamais d'install silencieuse scriptée).
  - Story 6.3 (écran de fin + raccourci) : **done**. Écran de fin avec message de complétion + deux cases à cocher (raccourci Bureau / Menu Démarrer), création réelle du `.lnk` via PowerShell/`WScript.Shell` (pas de nouvelle dépendance pip). Revue de code a trouvé et corrigé 2 bugs réels : absence de gestion d'erreur (un PowerShell bloqué par une stratégie de groupe laissait l'assistant bloqué sans retour au joueur) et un risque d'injection/corruption via l'interpolation non échappée des chemins dans la commande PowerShell (corrigé avec des chaînes PowerShell à guillemets simples).
  - Story 6.5 (packaging PyInstaller de l'installeur) : **done**. `verselog-installer.exe` construit (`--onefile --windowed`) et publié sur la Release GitHub `v0.1.0-windows` existante, aux côtés de `verselog.exe`. Mis en avant comme téléchargement recommandé en premier (docs + les deux README), à la demande explicite de Léon pour aider les joueurs. **Vérification directe par capture d'écran impossible** : Smart App Control bloque le binaire fraîchement construit (même limitation déjà connue pour `verselog.exe`, Story 5.1) ; confirmé avec Léon qui a préféré ne pas désactiver Smart App Control pour ce test — confiance basée sur un build sans erreur et le code déjà vérifié par capture d'écran (Stories 6.1-6.3). Reconstruire le `verselog.exe` périmé de cette même release reste explicitement hors scope, à faire séparément.
  - Story 6.6 (recommandation matérielle légère, indépendante des prérequis) : **done**. Léon a remarqué que `verselog-installer.exe` pesait presque aussi lourd que `verselog.exe` (27,8 Mo vs 29,3 Mo) — en creusant, un vrai bug de logique est apparu en plus : l'étape benchmark de l'installeur chronométrait Tesseract/Ollama *avant* qu'ils soient installés, mesurant la vitesse d'un échec plutôt que de vraies performances. Remplacé par une heuristique RAM simple (≥ 8 Go → vision), et `PrerequisiteChecker` (Story 5.3) réécrit pour ne plus importer `pytesseract`/`ollama` (juste `subprocess` + `requests`, déjà une dépendance du projet). Revue de code a trouvé et corrigé 7 problèmes réels. Résultat : **`verselog-installer.exe` 27,8 Mo → 15,1 Mo (46% de moins)**, republié sur la Release GitHub existante.
  - Story 6.4 (fixer la flakiness Tk() des tests, projet entier) : **backlog**, amélioration d'infra de test, pas bloquante — c'est la seule story qui garde Epic 6 en `in-progress` plutôt que `done`. **L'installeur guidé lui-même (Stories 6.1-6.3, 6.5, 6.6) est maintenant fonctionnellement complet, léger, empaqueté et publié.**
- Pages de revue de projet (`docs/project-review.html`/`-fr.html`) mises à jour le 2026-07-13 pour couvrir Epics 4, 5 et 6 (étaient restées figées à "3 epics" depuis avant le début de cette session), rafraîchies à nouveau après chaque story d'Epic 6 (6.2, 6.3, 6.5) pour éviter de re-tomber en retard — plus polish UX (scrollbar, section active en surbrillance, retour à la doc).

## Découvertes/limitations connues (non bloquantes)

- **Windows Smart App Control** peut bloquer `verselog.exe` (non signé) — pas de bouton "exécuter quand même", il faut le désactiver temporairement dans Sécurité Windows. Documenté dans les notes de Release et le README.
- **Tier vision (Ollama) gourmand en RAM** une fois réellement utilisé pour l'inférence — confirmé : fonctionne sur une VM à 4 Go tant que le modèle n'est pas chargé, plus du tout une fois utilisé. D'où Story 5.7.
- **Release Windows obsolète** (voir Story 5.1 ci-dessus) — à reconstruire avant toute nouvelle communication publique du lien de téléchargement Windows.
- **Flakiness d'environnement connue (non liée au code) :** créer beaucoup de fenêtres `tk.Tk()` réelles dans une même exécution de la suite de tests complète déclenche parfois une `TclError` transitoire à la construction — confirmé que ça touche plusieurs fichiers de tests pré-existants sans rapport entre eux (jamais le même deux fois de suite), pas un bug de code. Se résout en relançant les tests. Fix propre suivi en Story 6.4.

## Prochaine étape suggérée

Trois pistes possibles, aucune priorité imposée : (1) reconstruire/republier `verselog.exe` sur la même Release Windows pour inclure Stories 5.3/5.5/5.6 (le seul point encore périmé), (2) Story 5.8 (recherche filtrante pour la sélection du vaisseau, confirmée souhaitée par Léon), ou (3) autres stories backlog : 5.4, 5.7, 6.4.

## Où retrouver le contexte complet

- Documentation publiée : https://leonparquettept.github.io/VerseLog/
- Toutes les stories (détail complet de ce qui a été fait, comment, et pourquoi) : `_bmad-output/implementation-artifacts/*.md`
- État de toutes les stories (source de vérité) : `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Toutes les epics/stories, y compris le backlog : `_bmad-output/planning-artifacts/epics.md`
- Architecture : `_bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md`
- Contrat/spec du projet : `_bmad-output/specs/spec-verselog/SPEC.md`
