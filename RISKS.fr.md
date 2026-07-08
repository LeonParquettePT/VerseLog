# Risques & Mitigations

*[🇬🇧 Read in English](RISKS.md)*

Risques identifiés pendant la planification de VerseLog, pour que personne n'ait à les redécouvrir à la dure. Chaque entrée liste ce qui pourrait mal se passer, ce qu'on fait pour ça, et son statut actuel.

## Légal / Conditions d'utilisation

### Accepter automatiquement les contrats violerait l'EULA de CIG

L'EULA de CIG interdit explicitement les "logiciels d'automatisation (bots) ... conçus pour modifier l'expérience de jeu et/ou donner un avantage sur les autres joueurs." Calculer le meilleur contrat est acceptable (des calculateurs externes comme celui-ci sont tolérés dans la communauté) ; faire cliquer le logiciel sur "Accept" à la place du joueur ne l'est pas — ça bascule dans l'automatisation interdite.
- **Mitigation :** Non-goal, par conception. VerseLog n'injecte jamais d'input dans le jeu. Les recommandations s'affichent dans la fenêtre de VerseLog ; le joueur fait toujours l'action en jeu lui-même.
- **Statut :** Maîtrisé (règle architecturale dure, vérifiée contre le texte réel de l'EULA).

### Lire l'état/mémoire du jeu violerait aussi l'EULA

L'EULA de CIG interdit aussi séparément les logiciels qui "interceptent, minent, ou collectent autrement des informations depuis ou à travers le jeu." Ça a écarté une idée qu'on avait envisagée (un overlay en direct suivant la liste de contrats en jeu pendant qu'elle défile), puisqu'il aurait fallu lire la mémoire du jeu pour rester aligné.
- **Mitigation :** VerseLog ne lit que l'écran rendu (captures d'écran), jamais la mémoire du jeu ni le trafic réseau. L'idée d'overlay a été écartée au profit d'une fenêtre de résultats séparée.
- **Statut :** Maîtrisé.

### Déclencher un scan avec VoiceAttack est probablement correct, mais pas confirmé avec certitude

VoiceAttack simule une pression de touche (ex. un raccourci de capture d'écran) quand le joueur dit une commande — dans le même esprit qu'un bind HOTAS/manette, ce qui est courant et toléré. Ce n'est pas la même catégorie qu'une automatisation qui joue à la place du joueur, mais CIG n'a pas donné de feu vert explicite à VerseLog lui-même.
- **Mitigation :** Le déclenchement manuel est toujours disponible en repli, sans aucune ambiguïté. La voix est un confort optionnel, jamais obligatoire.
- **Statut :** Accepté (risque faible, pas éliminé).

## Dépendance tierce (api.star-citizen.wiki)

### Projet maintenu par une seule personne (facteur bus)

L'API communautaire dont VerseLog dépend pour les données de référence (vaisseaux, carburant, lieux) semble maintenue par essentiellement une seule personne.
- **Mitigation :** Un miroir hébergé indépendamment de l'API est prévu comme infrastructure optionnelle, pour que VerseLog ne soit pas bloqué si l'original disparaît.
- **Statut :** Mitigation prévue, pas encore construite.

### Limites de débit et conditions de réutilisation des données non publiées

Nous n'avons trouvé aucune limite de débit publiée ni condition explicite de réutilisation des données de jeu sous-jacentes (le code serveur de l'API est en MIT, mais ça ne couvre pas la donnée elle-même) dans un outil tiers.
- **Mitigation :** On avance sous une posture par défaut prudente — attribution claire, débit conservateur et auto-limité, usage strictement non-commercial et gratuit. La confirmation formelle avec le mainteneur est reportée, pas requise pour avancer.
- **Statut :** Ouvert, accepté comme risque faible vu le périmètre non-commercial et modeste du projet.

### Les données de trajet/distance ne sont pas précalculées par l'API

Les champs d'exemple de trajet par vaisseau de l'API sont une seule paire codée en dur sur Stanton, pas une vraie matrice de trajets, et ne couvrent ni Pyro ni les autres systèmes.
- **Mitigation :** VerseLog calcule lui-même le vrai coût point-à-point à partir des coordonnées des lieux et des stats de chaque vaisseau (voir Story 2.2).
- **Statut :** Maîtrisé (la conception en tient compte).

## Technique / Fiabilité

### Le jeu est en alpha — son interface peut changer sans prévenir

Un patch peut changer la mise en page de l'écran de contrats, cassant silencieusement l'extraction OCR/vision.
- **Mitigation :** La couche de confiance (validation + quarantaine) détecte les extractions mal formées au lieu de leur faire confiance aveuglément, et l'abstraction des fournisseurs permet de remplacer une méthode de capture cassée sans toucher au reste de l'app.
- **Statut :** Maîtrisé par conception ; il faut quand même s'attendre à de la casse occasionnelle après les gros patchs.

### Benchmark matériel trompeur

Faire le benchmark sur un PC au repos le fait paraître plus puissant qu'il ne l'est une fois le jeu réellement lancé, ce qui pourrait faire choisir un modèle trop lourd.
- **Mitigation :** Le benchmark doit s'exécuter pendant que Star Citizen tourne, pas à froid (voir Story 1.6).
- **Statut :** Maîtrisé par conception.

### Ajouter de la charge CPU sur un jeu déjà limité par le CPU

Star Citizen est exigeant, notamment côté CPU ; un outil d'aide qui entre en concurrence pour la même ressource va à l'encontre de son propre but pour les joueurs à PC modeste qu'il est censé aider en priorité.
- **Mitigation :** Chargement des modèles à la demande (en rafale, pas en continu), un pool de workers dimensionné par le benchmark, et un non-goal explicite contre toute fonctionnalité ajoutant une charge de fond soutenue.
- **Statut :** Maîtrisé par conception ; à vérifier en conditions réelles une fois construit.

## Projet / Maintenance

### Mainteneur solo et junior

Le projet est actuellement maintenu par une seule personne encore en train d'apprendre à coder.
- **Mitigation :** Open-source et collaboratif dès le premier jour pour que d'autres puissent lire, comprendre et reprendre le projet ; "fonctionnel d'abord, propre ensuite" garde le périmètre réaliste ; les artefacts de planification BMad Method (SPEC, architecture, epics) donnent à tout futur contributeur — ou à l'auteur lui-même après une pause — une carte claire pour revenir dans le projet.
- **Statut :** Accepté, activement mitigé.

### Le code produit avec l'aide d'une IA pourrait sembler de moindre qualité ou être source de méfiance dans la communauté open-source

Les contributeurs et utilisateurs peuvent être sceptiques envers du code assisté par IA.
- **Mitigation :** Conventions de code explicites dans `CONTRIBUTING.md` (code simple et direct, sans remplissage ni boilerplate) ; le projet est transparent sur son processus plutôt que de le cacher.
- **Statut :** Accepté, activement mitigé.
