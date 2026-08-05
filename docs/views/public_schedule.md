# Vue Publique — Horaires

> **Route** : `/events/{uuid}/schedule`  
> **Accès** : Public (aucune authentification requise)  
> **Lien depuis** : Page des résultats publics (en-tête)

---

## 1. Objectif

Permettre à quiconque disposant du lien de consulter les horaires de départ prévus des stagiaires inscrits à un événement.

---

## 2. Accès

- URL publique : `/events/{uuid}/schedule`
- **Aucune authentification** requise
- Accessible à tout moment

---

## 3. Structure de l'écran

### 3.1 En-tête

- **Nom de l'événement** affiché en haut de page
- **Titre** : "Horaires"
- **Lien retour** : "← Résultats" pointant vers `/events/{uuid}`
- **Lien conditionnel "← Vue encadrant"** : affiché uniquement si un token JWT valide (rôle `organizer`, non expiré) est présent en localStorage. Pointe vers `/admin/events/{uuid}/config` (onglet horaires). Discret (petit lien en haut à droite).

### 3.2 Tableau des horaires

Liste triée par **horaire croissant** (même ordre que l'onglet Horaires admin).

| Colonne | Contenu | Style |
|---------|---------|-------|
| **Horaire** | Heure de départ prévue (`start_time_planned`) | Texte gris |
| **Nom** | Prénom N. (anonymisé comme les autres vues publiques) | — |
| **Téléphone** | Numéro de téléphone | — |

> 💡 **Anonymisation** : comme toutes les vues publiques, le nom est affiché sous la forme "Prénom N." (première lettre du nom de famille + point).

---

## 4. Comportement

- Si aucun participant n'est inscrit, afficher un message : "Aucun participant inscrit"
- Les participants sans horaire planifié (`start_time_planned` null) apparaissent en fin de liste sans horaire affiché
- Le endpoint backend utilisé est `GET /api/public/events/{id}/schedule`

---

## 5. Données utilisées (en lecture)

| Donnée | Source |
|--------|--------|
| `registrations[].start_time_planned` | Configuration événement |
| `registrations[].user_id` | Configuration événement → résolution vers `users.json` |
| `users[].first_name` | Fichier users |
| `users[].last_name` | Fichier users (première lettre uniquement) |
| `users[].phone` | Fichier users |

---

## 6. Navigation

| Depuis | Vers | Lien |
|--------|------|------|
| Résultats publics | Cette page | Lien "📅 Horaires" dans l'en-tête |
| Cette page | Résultats publics | Lien "← Résultats" vers `/events/{uuid}` |

