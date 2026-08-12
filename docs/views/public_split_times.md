# Vue Publique — Comparaison des temps intermédiaires (Split Times)

> **Statut** : Brouillon  
> **Référence** : [Vue publique résultats](public_results.md)

---

## 1. Objectif

Permettre de comparer les temps intermédiaires (splits) de tous les concurrents, balise par balise, pour chaque paire de balises consécutives existante dans les parcours de l'événement.

---

## 2. Accès

- URL publique : `/events/{uuid}/splits`
- **Aucune authentification** requise
- Accessible depuis un lien dans l'en-tête de la [vue publique résultats](public_results.md)
- Accessible **à tout moment** (pas de restriction temporelle)

---

## 3. Concepts

### 3.1 Paire de balises

Une **paire de balises** est constituée de deux balises **consécutives** dans un parcours. Pour un parcours avec les balises [A, B, C, D], les paires sont : (A→B), (B→C), (C→D).

### 3.2 Paires uniques

Les paires sont extraites de **tous les parcours** de l'événement, puis dédupliquées. Si le parcours 1 a la paire (B3→B5) et le parcours 2 aussi, un seul tableau est affiché pour cette paire, contenant les concurrents des deux parcours.

### 3.3 Split time

Le **split time** d'un concurrent pour une paire (A→B) est le temps écoulé entre l'horaire de passage à la balise A et l'horaire de passage à la balise B.

- Pour la première balise du parcours (pas de balise précédente), le point de départ est l'**heure de départ réelle** du concurrent.

### 3.4 Horaire de passage d'une balise

L'horaire de passage utilisé est :
- Pour une balise PH (sauf la dernière) : l'horaire de **validation/départ** (checkpoint, pas ph_arrival)
- Pour une balise non-PH : l'horaire du checkpoint
- Pour la dernière PH : l'horaire du checkpoint (arrivée finale)

> 💡 C'est cohérent avec le calcul des temps intermédiaires de la vue résultats publique ([public_results.md §4.5](public_results.md)).

---

## 4. Structure de l'écran

### 4.1 En-tête

| Élément | Détail |
|---------|--------|
| **Lien retour** | **"← Retour aux résultats"** — retour vers la vue résultats publique (`/events/{uuid}`) |
| **Nom de l'événement** | Affiché en haut |
| **Titre de la page** | **"Comparaison des temps intermédiaires"** |
| **Lien conditionnel "← Vue encadrant"** | Affiché uniquement si token JWT organizer valide. Pointe vers `/admin/events/{uuid}/resultats` |

### 4.2 Corps — Un tableau par paire de balises

Pour chaque paire de balises, un bloc contenant :

#### Titre du bloc

Format : **"Balise {number}-{tag} → Balise {number}-{tag}"**

Exemples :
- "Départ → Balise 1-unique"
- "Balise 1-unique → Balise 2-NO"
- "Balise 3-unique → Balise 5-unique"

> 💡 La première paire de chaque parcours a pour origine le "Départ" (pas une balise).

#### Tableau

| Colonne | Contenu |
|---------|---------|
| **#** | Classement (rang) dans cette paire (1, 2, 3…) |
| **Concurrent** | Prénom N. (initiale du nom + point) |
| **Parcours** | Numéro du parcours |
| **Split** | Temps intermédiaire au format **MM:SS** ou **H:MM:SS** si ≥ 1h |

**Tri** : par split time croissant (le plus rapide en premier).

**Classement** : les concurrents avec le même split ont le même rang. Le rang suivant tient compte des ex-æquo (ex : 1, 2, 2, 4).

---

## 5. Ordre des tableaux

Les tableaux (paires de balises) sont ordonnés par :
1. **Numéro de la 1ère balise** (croissant) — "Départ" est considéré comme numéro 0
2. **Tag de la 1ère balise** (alphabétique)
3. **Numéro de la 2ème balise** (croissant)
4. **Tag de la 2ème balise** (alphabétique)

---

## 6. Filtrage des concurrents

Un concurrent apparaît dans un tableau de paire (A→B) **uniquement si** :
- Il a un **horaire de passage** renseigné pour les **deux** balises de la paire (ou un horaire de départ pour la première paire)
- Les horaires sont valides (le split calculé est > 0)

Les concurrents sans horaire sur l'une des deux balises sont **exclus** du tableau (pas de ligne vide).

> 💡 Aucune restriction liée au statut "arrivé" : un concurrent en cours d'épreuve peut apparaître dans les paires déjà complétées.

---

## 7. Données utilisées (en lecture)

| Donnée | Source |
|--------|--------|
| Liste des parcours + balises ordonnées | Configuration événement |
| Horaires de passage par balise | Logs des concurrents (état reconstruit) |
| Heure de départ réelle | Logs des concurrents (departure) |
| Identité des concurrents (prénom, nom) | Inscriptions événement |
| Parcours de chaque concurrent | Inscriptions événement |

---

## 8. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Vue publique résultats** | Page parente — lien retour + lien d'accès |
| **Résultats (encadrants)** | Utilise les mêmes données de base (horaires de passage) |


