# Contribuer à VerseLog

*[🇬🇧 Read in English](CONTRIBUTING.md)*

VerseLog est ouvert dès le départ pour que n'importe qui puisse le lire, le comprendre et l'améliorer — y compris des personnes qui, comme l'auteur du projet lui-même, sont encore en train d'apprendre. Pas besoin d'être expert pour contribuer ; il faut par contre lire [`SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md) d'abord (en anglais), car c'est le contrat auquel chaque changement doit se rattacher.

## Règles de base

- **Fonctionnel avant tout, propre ensuite.** Un changement qui marche et qui est correct vaut mieux qu'une belle abstraction. N'ajoute pas de flexibilité ou de design patterns pour des problèmes que le projet n'a pas encore.
- **Écris du code simple et direct.** Ne commente que ce que le code ne peut pas dire par lui-même (une contrainte non évidente, un contournement, un "pourquoi", pas un "quoi"). Évite le code de remplissage, la gestion défensive de cas qui ne peuvent pas arriver, et le fait de répéter l'évident — un code qui a l'air rembourré inspire moins confiance et est plus dur à maintenir, que ce soit un humain ou une IA qui l'ait écrit.
- **Respecte les contraintes du SPEC.md.** En particulier : pas de dépendance cloud payante, doit rester utilisable sur du matériel modeste, pas d'obligation de micro/commande vocale.

## Proposer un changement

1. Ouvre d'abord une issue pour tout ce qui n'est pas trivial, pour qu'on discute de l'approche avant d'écrire le code.
2. Fork le repo, crée une branche depuis `main`, fais ton changement.
3. Ouvre une pull request en décrivant *ce qui* a changé et *pourquoi* — renvoie vers la capacité du SPEC concernée (ex. `CAP-4`) ou la question ouverte, si applicable.
4. Sois patient — c'est un petit projet communautaire, les revues peuvent prendre un peu de temps.

## Signaler un bug

Ouvre une issue GitHub avec ce que tu attendais, ce qui s'est passé à la place, et ton environnement (OS, et si tu es sur Windows ou Linux — les deux sont supportés).

## Instructions d'installation

Pas encore écrites — la stack technique n'est pas encore figée. Cette section sera complétée une fois que ce sera fait.

## Licence

En contribuant, tu acceptes que ta contribution soit sous la [licence MIT](LICENSE) du projet.
