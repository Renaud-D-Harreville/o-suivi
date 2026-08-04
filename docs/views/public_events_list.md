# Vue — Liste des événements publics

> **Route** : `/events`  
> **Accès** : Public (aucune authentification requise)  
> **Lien depuis** : Page de login (lien en bas du formulaire)

---

## Objectif

Permettre à quiconque (stagiaires, visiteurs) de trouver un événement et d'accéder à ses résultats publics sans avoir besoin de connaître l'URL directe.

---

## Contenu

- **Titre** : "Événements publics"
- **Liste** de tous les événements existants
- **Tri** : par date d'événement (`date`) décroissante (plus récent en premier). Les événements sans date apparaissent en fin de liste.
- Chaque item affiche :
  - La **date** (si renseignée) en gris clair, affichée en premier
  - Le **nom** de l'événement, affiché après la date
- Chaque item est un **lien cliquable** vers `/events/:id` (résultats publics de l'événement)

---

## Comportement

- Si aucun événement n'existe, afficher un message : "Aucun événement disponible"
- La page est entièrement publique (pas de token requis)
- Le endpoint backend utilisé est `GET /api/public/events` (retourne la liste des EventSummary)

---

## Navigation

- Accessible depuis la page de login via un lien "Événements publics" en bas du formulaire
- Depuis cette page, retour vers la page de login via un lien "Connexion encadrant"
- **Lien conditionnel "← Vue encadrant"** : affiché uniquement si un token JWT valide (rôle `organizer`, non expiré) est présent en localStorage. Pointe vers `/admin`. Discret (petit lien en haut à droite).


