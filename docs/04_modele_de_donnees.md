# Modèle de Données — O-Suivi

> **Version** : 2.0  
> **Date** : 2026-07-24  
> **Auteur** : Renaud D'Harreville  
> **Statut** : Brouillon

---

## 1. Principes

- **Stockage** : fichiers JSON (pas de BDD relationnelle)
- **Données de configuration** : édition in-place, last write wins, pas d'historique
- **Données d'épreuve** : event sourcing léger (log append-only par inscription), `creation_date` wins pour la résolution de conflits

---

## 2. Structure des fichiers

```
data/
├── users.json                              ← Tous les utilisateurs (encadrants + stagiaires)
├── templates/
│   └── {template_id}.json                  ← Un fichier par template de probatoire
└── events/
    └── {event_id}/
        ├── event.json                      ← Configuration de l'événement (infos, balises, parcours, temps PH, inscriptions)
        └── logs/
            └── {user_id}.json              ← Log d'épreuve par inscrit (event sourcing)
```

---

## 3. Fichiers de configuration (sans historique)

### 3.1 `users.json`

```json
[
  {
    "id": "uuid",
    "username": "renaud",
    "password": "secret",
    "routechoices_id": null,
    "role": "organizer",
    "first_name": "Renaud",
    "last_name": "D'Harreville",
    "phone": "06 12 34 56 78",
    "sex": null
  },
  {
    "id": "uuid",
    "username": null,
    "password": null,
    "routechoices_id": "rc_67890",
    "role": "competitor",
    "first_name": "Marie",
    "last_name": "Dupont",
    "phone": "06 98 76 54 32",
    "sex": "F"
  }
]
```

> ⚠️ Les mots de passe sont stockés **en clair** pour le moment (phase développement). Une migration vers bcrypt est prévue avant la mise en production.

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique interne |
| `username` | string \| null | Identifiant de connexion (encadrants uniquement) |
| `password` | string \| null | Mot de passe en clair (encadrants uniquement) — TODO: bcrypt avant production |
| `routechoices_id` | string \| null | Identifiant Routechoices (unique, optionnel). Clé de déduplication fiable entre événements |
| `role` | `"organizer"` \| `"competitor"` | Rôle de l'utilisateur |
| `first_name` | string | Prénom |
| `last_name` | string | Nom |
| `phone` | string | Numéro de téléphone |
| `sex` | `"H"` \| `"F"` \| null | Sexe (non obligatoire) |

### 3.2 `templates/{template_id}.json`

```json
{
  "id": "uuid",
  "name": "Chartreuse 2026",
  "beacons": [
    { "id": 31, "number": 1, "tag": "unique", "is_ph": false },
    { "id": 32, "number": 2, "tag": "NO", "is_ph": false },
    { "id": 33, "number": 2, "tag": "SE", "is_ph": false },
    { "id": 34, "number": 3, "tag": "unique", "is_ph": true }
  ],
  "courses": [
    {
      "number": 1,
      "beacons": [31, 32, 34]
    }
  ],
  "time_gates": [
    {
      "course_number": 1,
      "gates": [
        { "gate": "PH1", "min_m": 45, "max_m": 75, "min_f": 45, "max_f": 85 },
        { "gate": "PH2", "min_m": 30, "max_m": 60, "min_f": 30, "max_f": 70 }
      ]
    }
  ]
}
```

> 💡 Le champ `is_ph` est un booléen : `true` si la balise est une porte horaire, `false` sinon. Le numéro de PH (PH1, PH2, ...) est calculé dynamiquement selon l'ordre de la balise PH dans le parcours.

> 💡 Le nombre d'entrées dans `gates[]` dépend du nombre de balises `is_ph: true` présentes dans le parcours. Le label `gate` ("PH1", "PH2", ...) est un identifiant ordinal : `gates[0]` = PH1, `gates[1]` = PH2, etc.

### 3.3 `events/{event_id}/event.json`

```json
{
  "id": "uuid",
  "name": "Proba Blanc Septembre 2026",
  "date": "2026-09-15",
  "template_id": "uuid",
  "first_start_time": "07:30",
  "routechoices_url": "https://www.routechoices.com/event/...",
  "public_routechoices_time": "14:00",
  "start_mode": { "group_size": 1, "interval_seconds": 120 },
  "beacons": [
    { "id": 31, "number": 1, "tag": "unique", "is_ph": false, "code": "AB" },
    { "id": 32, "number": 2, "tag": "NO", "is_ph": false, "code": "CD" },
    { "id": 33, "number": 2, "tag": "SE", "is_ph": false, "code": "EF" },
    { "id": 34, "number": 3, "tag": "unique", "is_ph": true, "code": "GH" }
  ],
  "courses": [
    {
      "number": 1,
      "beacons": [31, 32, 34]
    }
  ],
  "time_gates": [
    {
      "course_number": 1,
      "gates": [
        { "gate": "PH1", "min_m": 50, "max_m": 83, "min_f": 49, "max_f": 94 },
        { "gate": "PH2", "min_m": 32, "max_m": 63, "min_f": 32, "max_f": 74 },
        { "gate": "PH3", "min_m": null, "max_m": 52, "min_f": null, "max_f": 64 }
      ]
    }
  ],
  "registrations": [
    {
      "user_id": "uuid",
      "course_number": 1,
      "start_order": 1,
      "start_time_planned": "07:30",
      "tracker_number": "12"
    }
  ]
}
```

> 💡 `beacons`, `courses` et `time_gates` sont **copiés** depuis le template à la création de l'événement, puis indépendants.

> 💡 Chaque balise possède un **`id`** unique (entier auto-incrémenté à partir de 31, pour éviter la confusion avec les numéros de balises qui vont de 1 à ~20). Les parcours (`courses[].beacons`) référencent les balises par cet `id` au lieu de dupliquer les champs `number` et `tag`. Les endpoints GET de l'API enrichissent les références pour restituer les informations complètes de chaque balise (number, tag, is_ph).

---

## 4. Fichiers d'épreuve — Log (avec historique)

### 4.1 `events/{event_id}/logs/{user_id}.json`

Fichier **append-only** : chaque entrée est un événement ajouté à la fin. Le fichier n'est **pas trié** à l'écriture. L'état actuel est reconstruit en triant dynamiquement par `metadata.creation_date` à la lecture.

Structure d'un log entry :

```json
{
  "log_type": "<type>",
  "metadata": {
    "creation_date": "ISO 8601 — quand l'action s'est produite (horloge client)",
    "received_at": "ISO 8601 — quand le serveur a reçu l'entrée",
    "author_id": "uuid — qui a effectué l'action"
  },
  "data": { "..." }
}
```

> 💡 L'API GET ajoute dynamiquement un champ `author_name` (résolu depuis `author_id`) à la lecture. Ce champ n'est **pas stocké** dans le fichier JSON.

Exemple complet :

```json
[
  {
    "log_type": "departure",
    "metadata": {
      "creation_date": "2026-09-15T07:30:12Z",
      "received_at": "2026-09-15T07:30:13+00:00",
      "author_id": "uuid_encadrant"
    }
  },
  {
    "log_type": "checkpoint",
    "metadata": {
      "creation_date": "2026-09-15T07:45:03Z",
      "received_at": "2026-09-15T07:45:04+00:00",
      "author_id": "uuid_stagiaire"
    },
    "data": { "sequence": 1, "code": "AB" }
  },
  {
    "log_type": "ph_arrival",
    "metadata": {
      "creation_date": "2026-09-15T08:15:44Z",
      "received_at": "2026-09-15T08:15:45+00:00",
      "author_id": "uuid_stagiaire"
    },
    "data": { "sequence": 3 }
  },
  {
    "log_type": "checkpoint_edit",
    "metadata": {
      "creation_date": "2026-09-15T11:00:00Z",
      "received_at": "2026-09-15T11:00:01+00:00",
      "author_id": "uuid_encadrant"
    },
    "data": { "sequence": 1, "code": "AC", "passage_time": "2026-09-15T07:45:00Z", "comment": "Erreur de saisie" }
  },
  {
    "log_type": "abandon",
    "metadata": {
      "creation_date": "2026-09-15T09:30:00Z",
      "received_at": "2026-09-15T09:30:01+00:00",
      "author_id": "uuid_encadrant"
    },
    "data": { "comment": "Blessure au genou" }
  },
  {
    "log_type": "bag_weight",
    "metadata": {
      "creation_date": "2026-09-15T07:25:00Z",
      "received_at": "2026-09-15T07:25:01+00:00",
      "author_id": "uuid_stagiaire"
    },
    "data": { "moment": "start", "weight_kg": 8.5 }
  },
  {
    "log_type": "tracker_returned",
    "metadata": {
      "creation_date": "2026-09-15T11:15:00Z",
      "received_at": "2026-09-15T11:15:01+00:00",
      "author_id": "uuid_encadrant"
    },
    "data": { "tracker_number": "12" }
  }
]
```

### 4.2 Types d'événements dans le log

| `log_type` | Auteur | Data | Description |
|------|--------|-----------------------------------------|-------------|
| `departure` | encadrant | — | Départ confirmé (heure réelle = `metadata.creation_date`) |
| `departure_cancel` | encadrant | — | Annulation du départ |
| `departure_edit` | encadrant | `{ departure_time }` | Correction de l'heure de départ |
| `checkpoint` | stagiaire ou encadrant | `{ sequence, code }` | Code balise saisi (heure de passage = `metadata.creation_date`) |
| `checkpoint_edit` | encadrant ou public | `{ sequence, code?, passage_time?, comment? }` | Correction d'un checkpoint (`passage_time` = horaire de passage corrigé, distinct de `metadata.creation_date`) |
| `ph_arrival` | stagiaire ou encadrant | `{ sequence }` | Arrivée à la PH (étape 1) |
| `ph_arrival_edit` | encadrant ou public | `{ sequence, passage_time }` | Correction de l'heure d'arrivée à une PH |
| `skip` | stagiaire ou encadrant | `{ checkpoint }` | Saut d'une balise |
| `skip_cancel` | stagiaire ou encadrant | `{ checkpoint }` | Annulation d'un saut |
| `abandon` | encadrant | `{ comment }` | Marqué comme abandon |
| `abandon_cancel` | encadrant | `{ comment }` | Annulation de l'abandon |
| `dns` | encadrant | `{ comment }` | Marqué absent |
| `dns_cancel` | encadrant | `{ comment }` | Annulation du DNS |
| `bag_weight` | stagiaire ou encadrant | `{ moment: "start"\|"end", weight_kg }` | Poids du sac |
| `tracker_returned` | encadrant | `{ tracker_number }` | Tracker rendu |
| `tracker_returned_cancel` | encadrant | — | Annulation rendu tracker |

---

## 5. Reconstruction de l'état

Pour obtenir l'état actuel d'un inscrit, on relit le log, on le **trie dynamiquement par `metadata.creation_date`**, et on applique les règles :

- Chaque sous-classe de log implémente `apply_to(state)` (polymorphisme)
- `checkpoint_edit` sur une `sequence` → remplace le `checkpoint` de cette séquence
- `abandon_cancel` → annule le dernier `abandon`
- `skip_cancel` → annule le dernier `skip` correspondant
- `departure_cancel` → annule le `departure`
- `dns_cancel` → annule le `dns`
- `tracker_returned_cancel` → annule le `tracker_returned`

---

## 6. Résolution de conflits offline

1. Un appareil en mode offline accumule des événements dans un log local (IndexedDB)
2. Au retour réseau, les événements sont envoyés au serveur via `POST .../registrations/{uid}/log` (en liste)
3. Le serveur **ajoute** les entrées à la fin du fichier (append-only, pas de tri à l'écriture)
4. Chaque entrée reçoit un `received_at` (horodatage serveur) pour traçabilité
5. **Déduplication** : si une entrée avec le même `creation_date + type + sequence` existe déjà, elle est ignorée
6. En cas de conflit sur la même séquence (ex: deux `checkpoint` pour la séquence 5), le `creation_date` le plus récent fait foi (résolu dynamiquement au tri)
7. L'historique complet est conservé — les encadrants peuvent voir et corriger si nécessaire
