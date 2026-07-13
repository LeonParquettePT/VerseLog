# VerseLog

*[🇬🇧 Read in English](README.md)*

Un assistant logistique gratuit, open-source et collaboratif pour [Star Citizen](https://robertsspaceindustries.com/). VerseLog lit ton tableau de contrats, vérifie ce qu'il lit, et te renvoie un plan de trajet et de chargement qui maximise les aUEC gagnés par minute — conçu pour tourner à côté du jeu sur du matériel modeste, pas pour lui voler ses ressources.

## État du projet

Le cœur logique, les adaptateurs de capture/source de données, le point d'entrée applicatif et une interface graphique Tkinter sont construits et testés (4 epics terminés, 114 tests) — voir la [documentation du projet](https://leonparquettept.github.io/VerseLog/) pour la revue complète. Des versions packagées sont disponibles dès maintenant pour Windows et Linux, un seul fichier, pas besoin d'installer Python (Tesseract et Ollama restent des installations séparées) :

- **[Télécharger verselog.exe (Windows)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-windows)** — Windows peut carrément bloquer le .exe via le **Contrôle intelligent des applications** ("nous n'avons pas pu vérifier son éditeur") puisque le binaire n'est pas encore signé — il n'y a pas de bouton "exécuter quand même" pour ce blocage-là. Il faut le désactiver temporairement (Sécurité Windows → Contrôle des applications et du navigateur) pour lancer l'app ; le réactiver ensuite risque de re-bloquer l'app au lancement suivant (elle reste non signée) — donc soit le laisser désactivé tant que tu utilises VerseLog, soit le basculer à chaque lancement. Voir les notes de la Release pour les détails.
- **[Télécharger verselog-linux (Linux)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-linux)** — construit via un environnement GitHub Actions jetable, vérifié en CI (se construit et s'exécute correctement en mode headless). Lance `chmod +x verselog-linux` après le téléchargement. La vérification manuelle que la fenêtre graphique s'affiche bien sur un vrai bureau Linux reste en attente — voir les notes de la Release.

Le contrat complet de ce que ce projet va construire se trouve dans [`_bmad-output/specs/spec-verselog/SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md) (en anglais). Les risques connus et comment on les gère sont suivis dans [RISKS.fr.md](RISKS.fr.md).

## Contribuer

Les contributions sont les bienvenues — ce projet est ouvert dès le départ pour que n'importe qui puisse le lire, le comprendre et l'améliorer. Consulte [`CONTRIBUTING.fr.md`](CONTRIBUTING.fr.md) pour les règles de base et comment proposer un changement.

## Licence

MIT — voir [LICENSE](LICENSE).
