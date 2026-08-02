# Événement — Onglet Horaires Participants

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.2](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Définir le mode de départ, l'ordre des concurrents et calculer automatiquement les horaires de départ de chaque participant.

---

## 2. Pré-requis

- L'heure du premier départ doit être renseignée dans l'onglet [Général](general.md)
- Des participants doivent être inscrits via l'onglet [Participants](participants.md)

---

## 3. Structure de l'écran

### 3.1 Configuration du mode de départ

| Champ | Type | Description | Défaut |
|-------|------|-------------|--------|
| **Personnes par départ** | nombre | Combien de personnes partent en même temps | 1 |
| **Intervalle** | nombre + unité (min/sec) | Temps entre chaque départ | 2 min |

> 💡 Presets rapides : "1 personne / 2 min" (défaut), "2 personnes / 3 min", ou personnalisé.

### 3.2 Tableau des participants ordonnés

Tableau ordonné des participants avec horaires et parcours calculés automatiquement :

| Colonne | Description |
|---------|-------------|
| **↕** | Poignée de drag & drop (monter/descendre) |
| **Ordre** | Numéro d'ordre (recalculé automatiquement) |
| **Nom / Prénom** | Identité du concurrent |
| **Sexe** | H / F |
| **Parcours** | Parcours attribué (numéro 1 à 6, calculé automatiquement, modifiable via dropdown) |
| **Horaire** | Heure de départ calculée automatiquement |

### 3.3 Wireframe

```
  Personnes par départ : [ 1 ]    Intervalle : [ 2 ] min
  
  [ 1/2min ]  [ 2/3min ]  [ Personnalisé ]     ← Presets rapides

┌────┬───────┬──────────────────┬──────┬────────────┬─────────┐
│ ↕  │ Ordre │ Nom / Prénom     │ Sexe │ Parcours   │ Horaire │
├────┼───────┼──────────────────┼──────┼────────────┼─────────┤
│ ≡  │   1   │ Dupont Marie     │  F   │ [▼ 1     ] │  07:30  │
│ ≡  │   2   │ Leroy Julie      │  F   │ [▼ 2     ] │  07:32  │
│ ≡  │   3   │ Martin Pierre    │  H   │ [▼ 3     ] │  07:34  │
│ ≡  │   4   │ Bernard Thomas   │  H   │ [▼ 4     ] │  07:36  │
│ ≡  │   5   │ Moreau Sophie    │  F   │ [▼ 1     ] │  07:38  │
│ ≡  │   6   │ Petit Luc        │  H   │ [▼ 2     ] │  07:40  │
├────┴───────┴──────────────────┴──────┴────────────┴─────────┤
│                                          [ Enregistrer ]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Actions

| Action | Description |
|--------|-------------|
| **Drag & drop** | Déplacer un participant pour changer son ordre de départ |
| **Modifier le parcours** | Dropdown par participant |
| **Modifier le mode de départ** | Recalcule tous les horaires automatiquement |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Comportements automatiques

### 5.1 Tri initial

À la première génération (après import des participants) :
- **Femmes en premier**, puis hommes
- Au sein de chaque groupe : ordre alphabétique

### 5.2 Attribution des parcours

- Attribution **cyclique** : 1, 2, 3, 4, 1, 2, 3, 4… dans l'ordre de la liste (le nombre de parcours dépend du template)
- Recalculée automatiquement quand l'ordre des participants change (drag & drop)
- Modifiable manuellement par l'encadrant (dropdown)

### 5.3 Calcul des horaires et parcours

- Les horaires **et** les parcours sont recalculés ensemble quand :
  - Le mode de départ change
  - L'heure du premier départ change
  - Un concurrent est déplacé (drag & drop)
- Cela garantit que les parcours restent dans l'ordre (1, 2, 3, 4…) pour faciliter la distribution des cartes par les organisateurs

---

## 6. Règles métier

- L'ordre de départ et les horaires restent modifiables à tout moment (y compris pendant l'épreuve, via la [vue Départ](../depart.md))
- Le parcours attribué est modifiable à tout moment
- L'horaire affiché est l'horaire **prévu** — l'heure réelle de départ est enregistrée lors du clic "Départ" dans la vue Départ

