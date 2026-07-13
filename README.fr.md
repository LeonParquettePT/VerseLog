# VerseLog

*[🇬🇧 Read in English](README.md)*

Un assistant logistique gratuit, open-source et collaboratif pour [Star Citizen](https://robertsspaceindustries.com/). VerseLog lit ton tableau de contrats, vérifie ce qu'il lit, et te renvoie un plan de trajet et de chargement qui maximise les aUEC gagnés par minute — conçu pour tourner à côté du jeu sur du matériel modeste, pas pour lui voler ses ressources.

## État du projet

Le cœur logique, les adaptateurs de capture/source de données, le point d'entrée applicatif, une interface graphique Tkinter et un installeur guidé pour Windows sont construits et testés (4 epics terminés, 25 stories, 176 tests) — voir la [documentation du projet](https://leonparquettept.github.io/VerseLog/) pour la revue complète. Des versions packagées sont disponibles dès maintenant pour Windows et Linux, un seul fichier, pas besoin d'installer Python (Tesseract et Ollama restent des installations séparées) :

- **[Télécharger verselog-installer.exe (Windows, recommandé)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-windows)** — un installeur guidé étape par étape : fait tourner un benchmark matériel, te laisse choisir quels prérequis installer (cases à cocher, rien n'est installé sans ta confirmation), et propose de créer un raccourci à la fin. Place-le dans le même dossier que `verselog.exe`.
- **[Télécharger verselog.exe (Windows, direct)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-windows)** — pour sauter l'assistant et lancer directement l'application elle-même.
- L'un ou l'autre .exe peut être bloqué par le **Contrôle intelligent des applications** ("nous n'avons pas pu vérifier son éditeur") puisqu'aucun des deux binaires n'est encore signé — il n'y a pas de bouton "exécuter quand même" pour ce blocage-là. Il faut le désactiver temporairement (Sécurité Windows → Contrôle des applications et du navigateur) pour lancer l'app ; le réactiver ensuite risque de re-bloquer l'app au lancement suivant (elle reste non signée) — donc soit le laisser désactivé tant que tu utilises VerseLog, soit le basculer à chaque lancement. Voir les notes de la Release pour les détails.
- **[Télécharger verselog-linux (Linux)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-linux)** — construit via un environnement GitHub Actions jetable, vérifié de bout en bout sur une vraie VM Ubuntu Desktop (fenêtre graphique comprise). Lance `chmod +x verselog-linux` après le téléchargement. Voir les notes de la Release pour un bloc de commandes d'installation copiable-collable.

Remarque : faire tourner le tier de vision local (Ollama) demande beaucoup de RAM dès qu'il est réellement utilisé pour l'inférence — confirmé directement sur une VM de test à 4 Go (ça passe tant que le modèle n'est pas chargé, plus du tout une fois qu'il l'est). Le benchmark intégré devrait déjà privilégier le tier Tesseract/OCR, plus léger, sur du matériel modeste.

Le contrat complet de ce que ce projet va construire se trouve dans [`_bmad-output/specs/spec-verselog/SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md) (en anglais). Les risques connus et comment on les gère sont suivis dans [RISKS.fr.md](RISKS.fr.md).

## Contribuer

Les contributions sont les bienvenues — ce projet est ouvert dès le départ pour que n'importe qui puisse le lire, le comprendre et l'améliorer. Consulte [`CONTRIBUTING.fr.md`](CONTRIBUTING.fr.md) pour les règles de base et comment proposer un changement.

## Licence

MIT — voir [LICENSE](LICENSE).
