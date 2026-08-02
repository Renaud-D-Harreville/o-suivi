# Événement — Vue d'ensemble

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.2](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Configurer un événement (probatoire blanc) à partir d'un template de probatoire. L'événement ajoute les participants, les horaires, les codes balises et les éventuels ajustements de temps PH.

---

## 2. Accès

Encadrants uniquement. Accessible depuis la [page d'accueil admin](../admin_home.md) (onglet Événements).

---

## 3. Structure de l'écran

### 3.1 En-tête

- **Nom de l'événement** (affiché, modifiable inline)

### 3.2 Navigation par onglets (6 onglets)

```
┌──────────┬──────────────┬──────────────────┬──────────────────┬──────────────┬───────────────────┐
│ GÉNÉRAL  │   BALISES    │    PARCOURS      │  PARTICIPANTS    │   HORAIRES   │ BARRIÈRES HORAIRES│
└──────────┴──────────────┴──────────────────┴──────────────────┴──────────────┴───────────────────┘
```

| Onglet | Fichier | Description |
|--------|---------|-------------|
| Général | [general.md](general.md) | Nom, date, template, lien Routechoices, heure premier départ |
| Balises | [beacons.md](beacons.md) | Registre des balises + codes 2 lettres (copié du template, indépendant) |
| Parcours | [courses.md](courses.md) | Construction des parcours (copié du template, indépendant) |
| Participants | [participants.md](participants.md) | Import/ajout/édition des participants inscrits |
| Horaires | [schedule.md](schedule.md) | Ordre de départ, mode de départ, horaires et parcours calculés |
| Barrières horaires | [time_gates.md](time_gates.md) | Ajustement des temps PH pour cet événement |

---

## 4. Navigation entre vues événement

Chaque vue événement (Config, Départ, Suivi, Résultats) partage un **header commun sticky** :

```
┌─────────────────────────────────────────────────────────────┐
│  ← Retour    Proba Blanc Sept 2026                          │
│  [ Config ]  [ Départ ]  [ Suivi ]  [ Résultats ]          │
└─────────────────────────────────────────────────────────────┘
```

| Élément | Description |
|---------|-------------|
| ← Retour | Ramène à la page d'accueil admin |
| Nom de l'événement | Affiché en titre |
| 4 boutons de navigation | Liens vers les 4 vues événement. Le bouton actif est mis en évidence |

**Routes correspondantes :**

| Bouton | Route |
|--------|-------|
| Config | `/admin/events/:id/config` |
| Départ | `/admin/events/:id/depart` |
| Suivi | `/admin/events/:id/suivi` |
| Résultats | `/admin/events/:id/resultats` |

---

## 5. Flux de configuration typique

1. **Général** : sélectionner le template, renseigner la date et l'heure
2. **Participants** : importer ou ajouter les concurrents
3. **Horaires** : définir le mode de départ, ordonner les concurrents
4. **Codes balises** : attribuer les codes 2 lettres (peut être fait tardivement, y compris le jour J)
5. **Barrières horaires** : ajuster les temps PH si nécessaire

> 💡 L'utilisateur peut naviguer librement entre les onglets. Cette page reste accessible tout au long de l'événement pour modifications.
