# O-Suivi

Application web de gestion de **probatoires blancs d'orientation** pour la formation AMM (Accompagnateur en Moyenne Montagne).

Remplace le suivi par tableur (Google Sheets) par une application dédiée : configuration d'événements, gestion des départs, suivi temps réel des concurrents, et affichage des résultats.

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Vue.js 3 (PWA) + Vite |
| Backend | Python / FastAPI |
| Stockage | Fichiers JSON |
| Hébergement | GCP (Cloud Run / GCE) |

## Lancer l'application

### Pré-requis

- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/install/)

### Démarrage

```bash
docker compose up --build
```

L'application est accessible sur :

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000     |
| Backend  | http://localhost:8000       |
| API docs | http://localhost:8000/docs  |

### Arrêt

```bash
docker compose down
```

## Documentation

Toute la documentation est dans le dossier `docs/` :

| Document | Description |
|----------|-------------|
| [Cahier des charges fonctionnel](docs/01_cahier_des_charges_fonctionnel.md) | Besoins métier et périmètre fonctionnel |
| [Spécifications techniques](docs/03_specifications_techniques.md) | Architecture, API, stack, stratégie offline |
| [Modèle de données](docs/04_modele_de_donnees.md) | Structure des fichiers JSON et event sourcing |
| [Spécifications des vues](docs/views/) | Specs détaillées par écran (départ, suivi, résultats…) |
| [Backlog](docs/backlog.md) | Fonctionnalités reportées et idées futures |
| [Decisions](docs/decisions.md) | Journal des décisions architecturales |

Pour les agents IA : voir [`agents.md`](agents.md).
