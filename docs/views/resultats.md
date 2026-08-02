# Vue Résultats Provisoires (Encadrants + Stagiaires)

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.4](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Afficher un récapitulatif clair de la performance de chaque concurrent après l'épreuve.

---

## 2. Accès

- **Encadrants** : accessible à tout moment pendant et après l'épreuve
- **Stagiaires** : accessible **après la fin de leur propre épreuve** (une fois arrivés + tracker rendu si applicable). Ils voient les résultats de **l'ensemble des stagiaires**
- **Public** : une vue publique alternative existe via `/events/{uuid}` (voir [public_results.md](public_results.md)) — accessible sans authentification, à tout moment

---

## 3. Structure de l'écran

### 3.1 En-tête

- **Lien Routechoices** : lien externe unique vers l'événement Routechoices (traces GPS de tous les concurrents). Renseigné par les organisateurs lors de la configuration.

### 3.2 Liste des concurrents

Liste triée par **ordre d'arrivée** (heure de validation de la dernière PH, les premiers arrivés en haut). Les DNS sont placés en fin de liste.

#### Structure d'une ligne concurrent (2 sous-lignes)

```
┌───────────────────────────────────────────────┐
│  Marie Dupont                             ✅  │  ← Ligne 1 : Prénom / Nom / Résultat global
│  PH1 ✅  PH2 ✅  PH3 ❌  …                    │  ← Ligne 2 : Statut par PH (nombre dynamique)
└───────────────────────────────────────────────┘
```

| Sous-ligne | Contenu |
|------------|---------|
| Ligne 1 | Prénom · Nom · Résultat global (✅ VALIDÉ / ❌ NON VALIDÉ) |
| Ligne 2 | PH1 · PH2 · PH3 · … · PHn — chacun avec ✅ (valide) ou ❌ (invalide) ou `-` (non atteint). Le nombre de PH affiché dépend du parcours du concurrent |

#### Cas particuliers

| Statut | Affichage |
|--------|-----------|
| **DNS** | Fond grisé, texte barré, **non cliquable**, placé en fin de liste |
| **Abandon** | Affichage normal, PH non atteintes marquées `-` |
| **Balises sautées (skip)** | Affichage normal, PH non atteintes marquées `-` |

---

## 4. Vue détaillée (dépliable, clic sur une ligne)

Au clic sur la ligne d'un concurrent, un panneau se déplie avec :

### 4.1 Informations générales

- **Poids du sac** : Départ / Arrivée
- **Heure de départ réelle** : horodatage du départ (prise en compte du retard éventuel)
- **Heure d'arrivée** : horodatage de l'arrivée

### 4.2 Résumé par section

| Information | Affichage |
|-------------|-----------|
| **Retard par PH** | Négatif si trop tôt (avant borne min), rien si dans les temps, positif si trop tard (après borne max) |
| **Temps par section** | Temps officiel entre chaque PH (validation à validation). C'est ce temps qui est comparé aux bornes min/max |
| **Temps de course (section)** | Temps de déplacement effectif sur la section, hors pause : validation PH(n-1) → arrivée PH(n) |
| **Temps de pause** | Temps entre l'arrivée à la PH et la validation/départ de la PH |
| **Temps en course (total)** | Somme de tous les temps de course de chaque section (temps de déplacement effectif, hors pauses) |
| **Temps total** | Heure d'arrivée (validation dernière PH) − heure de départ réelle. Inclut les pauses |

### 4.3 Liste détaillée des balises

Pour chaque balise du parcours du concurrent :

| Colonne | Contenu |
|---------|---------|
| **N°** | Numéro de la balise |
| **Code saisi** | Les 2 lettres saisies par le stagiaire |
| **Validité** | ✅ ou ❌ (code correct ou incorrect) |
| **Temps intermédiaire** | Temps écoulé entre la balise précédente et celle-ci |
| **Temps cumulé section** | Temps cumulé depuis le début de la section en cours |

---

## 5. Critères de validation

### 5.1 Validation globale

Un concurrent est **VALIDÉ** si et seulement si **toutes ses sections sont validées**.

### 5.2 Validation par section (PH)

Une section est **validée** (✅) si :

1. La PH est passée dans les temps (borne max obligatoire ; borne min si définie par l'organisateur)
2. Toutes les balises **de cette section** ont été validées (code correct)
3. Les balises de la section sont validées **dans le bon ordre**
4. Uniquement les balises de cette section (pas de balise d'un autre parcours)

Si **au moins un critère** de la section n'est pas respecté → section **non validée** (❌).

> 💡 Rappel : le proba blanc est un entraînement — un candidat "non validé" a quand même pu terminer le parcours (pas d'élimination en cours de route).

---

## 6. Données utilisées (en lecture)

| Donnée | Source |
|--------|--------|
| Codes saisis + horodatages | Logs des concurrents (saisie directe ou édition publique) |
| Heures d'arrivée / validation PH | Logs des concurrents (mécanisme PH) |
| Heure de départ réelle | Vue Départ |
| Bornes min/max par PH | Configuration (modèle probatoire) |
| Codes attendus par balise | Configuration (événement) |
| Poids du sac (départ/arrivée) | Logs des concurrents |
| Lien Routechoices | Configuration (événement) |

---

## 7. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Suivi** | Partage les mêmes données de base (codes, PH, temps) |
| **Configuration** | Fournit les bornes PH, les codes attendus et le lien Routechoices |
| **Vue publique résultats** | Même affichage, accès sans auth, avec lien vers édition balises ([public_results.md](public_results.md)) |
