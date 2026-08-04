# Backlog — O-Suivi

> Fonctionnalités retirées du périmètre v1 ou idées à explorer pour les versions futures.  
> Ce fichier sert de mémoire : rien ici n'est engagé, tout est à (re)valider avant intégration.

---

## V2 — Intégration GPS / Routechoices

> **Contexte** : L'intégration avec la plateforme Routechoices (tracking GPS en direct) a été retirée du périmètre v1 pour simplifier le développement initial. Les fonctionnalités ci-dessous pourront être réintroduites dans une version ultérieure.

### Glossaire associé

- **Routechoices** : Plateforme de tracking GPS en direct utilisée pour le suivi des concurrents en course d'orientation
- **Tracker** : Balise GPS portée par le concurrent, visible sur Routechoices

### Fonctionnalités retirées

#### Configuration (§5.1.1)

- **Coordonnées GPS** dans le registre des balises (champ optionnel latitude/longitude)
- **Rayon de détection automatique GPS** (en mètres) par balise/PH dans les parcours
- **N° Routechoices** dans le fichier d'import des participants

#### Vue Départ (§5.2)

- **Statut Routechoices** par concurrent : indicateur OK/pas OK (tracker actif et visible sur la plateforme)

#### Vue Suivi (§5.3)

- **Détection automatique de proximité GPS** : lorsqu'un concurrent entre dans un rayon défini autour d'une PH, le système signale sa proximité (couleur orange dans les pastilles PH)
- Cette détection était une **aide visuelle pour les encadrants**, pas une validation définitive

#### Vue Résultats (§5.4)

- **Trace GPS** : lien vers Routechoices pour visualiser le parcours réel du concurrent

#### Espace Stagiaire — Pré-départ (§5.5.1)

- **Statut Routechoices** : indicateur tracker OK/pas OK

#### Règle métier — Détection automatique GPS (§6.4)

- Lorsqu'un concurrent entre dans un **rayon défini** autour d'une PH (coordonnées GPS), le système signale sa proximité (couleur orange)
- Cette détection est une **aide visuelle pour les encadrants**, pas une validation définitive
- La validation définitive se fait par la saisie du code 2 lettres par le stagiaire, ou manuellement par un encadrant

#### Données & intégrations (§7)

- **Import** : champ "N° Routechoices" dans le fichier participants
- **Tracking GPS** : intégration API Routechoices comme source de données
- **Intégration Routechoices** (§7.3) :
  - Vérification de l'état du tracker (actif/inactif)
  - Récupération de la position GPS pour la détection automatique de proximité aux PH
  - Lien vers la trace GPS dans les résultats

#### Questions ouvertes associées

- [ ] Détails de l'API Routechoices (disponibilité, limitations, authentification)
- [ ] Rayon de détection optimal par type de balise (forêt dense vs. terrain ouvert)

---

## Améliorations frontend (issues review 2026-07-30)


### Signaler un abandon avec tracker

Un abandon d'une personne ayant un tracker doit pouvoir être signalé et suivi jusqu'à son rendu.

### Pinia — State management centralisé

- ✅ **Fait** (2026-07-30) : store `event-store.ts` créé, 4 vues admin refactorées, cache en mémoire actif. Dépendance `pinia` installée.

### WebSocket + bouton recharger — Temps réel dans la vue Suivi

- ✅ **Fait** (2026-07-30) : WebSocket avec reconnexion auto (backoff + visibility-aware), bandeau offline + bouton "Se reconnecter", signal "refresh" broadcasté depuis les endpoints de logs. Pas de polling en boucle.

### Dexie + PWA — Mode offline

Contrainte critique du projet (montagne sans réseau).
- ✅ **PWA fait** (2026-08-02) : `vite-plugin-pwa` installé, service worker Workbox (`generateSW`), precache assets, cache `NetworkFirst` API, manifest + icônes, `ReloadPrompt.vue`, meta tags PWA
- ✅ **Dexie.js fait** (2026-08-03) : IndexedDB via Dexie 4.x, file d'attente offline (`pendingActions`), cache événements (`eventCache`), sync engine (replay via endpoints individuels), indicateur réseau global, composable + composant UI

---

## Ajout d'une page pour les stagiaires

Les stagiaires doivent pouvoir accéder à une page web qui leur est dédiée, avec une page de connexion, une page qui liste les événéments auxquels ils sont ou ont été inscrits. 
Lorsqu'il sélectionne un événement, il doit pouvoir accéder à plusieurs pages / onglets lui permettant de :
- Renseigner les codes + horaires de passage aux balises (PH)
- Voir les résultats de la course.

## Amélioration de l'authentification utilisateur

Problèmes : 
- Les stagiaires n'ont pas de vrai 'compte' : ils n'ont pas de mot de passe, et il faut un lien un peu particulier pour qu'ils accèdent à leur espace.
- Les encadrants ont un compte classique, mais leur mot de passe est stocké en clair
- Il n'y a pas de mécanisme de réinitialisation de mot de passe
- pas de définition claire des pseudos pour la connexion, il faudrait regarder cela. 



## Corrections de code

> Incohérences ou problèmes techniques identifiés lors de la review, à corriger.

### CORS middleware

Ajouter `CORSMiddleware` dans `main.py` (FastAPI). Nécessaire pour la production (frontend et backend sur des origines différentes). 
Configurer les origines autorisées via variable d'environnement.

---

## Idées futures

> Espace libre pour noter des idées d'amélioration, sans engagement.

- [ ] ...

---

## À spécifier ultérieurement

> Points identifiés lors de la revue du cahier des charges, à détailler dans une prochaine itération.

### Consignes de sécurité dans l'espace stagiaire

`espace_stagiaire.md` §5.6.3 mentionne des "consignes globales de sécurité" affichées au stagiaire, mais aucun champ correspondant n'existe dans la configuration de l'événement. Il faudra ajouter un champ texte libre (ou un lien vers un document) dans l'onglet Général de l'événement pour permettre aux encadrants de saisir ces consignes.

### Bouton "Sauter des balises" dans la vue Suivi encadrant

Le mécanisme de skip de balises doit être accessible depuis la vue Suivi (côté encadrant), en plus de l'interface stagiaire. Il faut ajouter un bouton/champ dans le dépliant d'un concurrent (vue Suivi §4) qui permette à l'encadrant de skip des balises pour le compte d'un stagiaire.




## Réversibilité et mécanisme des balises sautées

- ✅ **Corrigé** (2026-07-27) : le skip est désormais balise par balise, réversible, avec `{ sequence }` dans le log. Les docs `espace_stagiaire.md`, `04_modele_de_donnees.md` et `03_specifications_techniques.md` ont été mis à jour.

---

## Vues à spécifier

### Vue Login (encadrants)

Page de connexion encadrant (`/login`). À spécifier : champs (pseudo + mot de passe), gestion d'erreur, design, lien retour vers l'événement si le stagiaire s'est trompé.

### Vue Sélection du nom (stagiaires)

Page de sélection du nom stagiaire (`/event/:id_event`). À spécifier : affichage de la liste des participants, recherche/filtrage, sélection, génération du JWT, bouton "Je suis encadrant" → `/login`.

### Consignes de sécurité (champ données)

`espace_stagiaire.md` §5.6.3 mentionne des "consignes globales de sécurité" affichées au stagiaire, mais aucun champ correspondant n'existe dans la configuration de l'événement. Il faudra ajouter un champ texte libre (ou un lien vers un document) dans l'onglet Général de l'événement pour permettre aux encadrants de saisir ces consignes.


