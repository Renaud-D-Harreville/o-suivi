# Événement — Onglet Parcours

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1 — Parcours](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Gérer les parcours de l'événement (copiés du template à la création, mais indépendants ensuite). Permet d'adapter les parcours aux conditions du jour.

---

## 2. Initialisation

Les parcours de l'événement sont importés depuis le template via le bouton **"Initialiser depuis le template"** dans l'onglet [Général](general.md). À partir de ce moment, les parcours de l'événement sont **indépendants** du template.

---

## 3. Structure de l'écran

Identique à l'onglet [Parcours du template](../templates/courses.md) : tableau en grille avec les numéros de balises en lignes et les parcours en colonnes.

### 3.1 Tableau parcours

| N° balise | Parcours 1 | Parcours 2 | Parcours 3 | Parcours 4 | ... |
|-----------|------------|------------|------------|------------|-----|
| 1 | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| 2 | ▼ NO | ▼ SE | ▼ NO | ▼ SE | |
| 3 (☑ PH) | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| 4 | ▼ N | ▼ S | ▼ N | ▼ S | |
| ... | ... | ... | ... | ... | |

### 3.2 Comportement des cellules

| Type de balise | Affichage | Interaction |
|----------------|-----------|-------------|
| **Unique** | Tag affiché, fond grisé | Non modifiable (pré-rempli) |
| **Avec variantes** | Dropdown avec les tags disponibles | Sélection d'une variante |

### 3.3 Wireframe

```
┌──────────┬────────────┬────────────┬────────────┬────────────┐
│ N°       │ Parcours 1 │ Parcours 2 │ Parcours 3 │ Parcours 4 │
├──────────┼────────────┼────────────┼────────────┼────────────┤
│ 1        │  unique    │  unique    │  unique    │  unique    │
│ 2        │ [▼ NO  ]   │ [▼ SE  ]   │ [▼ NO  ]   │ [▼ SE  ]   │
│ 3 (☑ PH) │  unique    │  unique    │  unique    │  unique    │
│ 4        │ [▼ N   ]   │ [▼ S   ]   │ [▼ N   ]   │ [▼ S   ]   │
│ 5        │  unique    │  unique    │  unique    │  unique    │
│ 6 (☑ PH) │  unique    │  unique    │  unique    │  unique    │
│ ...      │ ...        │ ...        │ ...        │ ...        │
├──────────┴────────────┴────────────┴────────────┴────────────┤
│  [ + Ajouter un parcours ]          [ Enregistrer ]          │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Actions

| Action | Description |
|--------|-------------|
| **Ajouter un parcours** | Ajoute une nouvelle colonne |
| **Supprimer un parcours** | Bouton ✗ en haut de la colonne |
| **Sélectionner une variante** | Dropdown dans chaque cellule à variantes |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Règles métier

- Chaque parcours doit avoir **exactement une variante** sélectionnée par numéro de balise
- Les balises `unique` sont automatiquement pré-remplies et non modifiables
- Les lignes (numéros de balises) sont déterminées par le registre de l'événement (onglet [Balises](beacons.md))
- **Modifiable à tout moment**, y compris pendant l'épreuve
- Le nombre de parcours impacte l'attribution cyclique dans l'onglet [Horaires](schedule.md)

> ⚠️ Modifier les parcours pendant l'épreuve impacte les concurrents en cours. L'encadrant doit en être conscient.

