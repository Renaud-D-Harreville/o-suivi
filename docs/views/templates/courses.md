# Template — Onglet Parcours

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1 — Parcours](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Construire les parcours (4 à 6) à partir du registre des balises. Chaque parcours est une sélection ordonnée de balises : une seule variante par numéro.

---

## 2. Pré-requis

Le [registre des balises](beacons.md) doit être rempli. Si le registre est vide, l'onglet affiche un message invitant à le compléter d'abord.

---

## 3. Structure de l'écran

### 3.1 Tableau parcours

Tableau en grille : les **lignes** sont les numéros de balises, les **colonnes** sont les parcours.

| N° balise | Parcours 1 | Parcours 2 | Parcours 3 | Parcours 4 | ... |
|-----------|------------|------------|------------|------------|-----|
| 1 | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| 2 | ▼ NO | ▼ SE | ▼ NO | ▼ SE | |
| 3 (☑ PH) | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| 4 | ▼ N | ▼ S | ▼ N | ▼ S | |
| 5 | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| 6 (☑ PH) | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | unique _(grisé)_ | |
| ... | ... | ... | ... | ... | |

### 3.2 Comportement des cellules

| Type de balise | Affichage | Interaction |
|----------------|-----------|-------------|
| **Unique** | Tag affiché, fond grisé | Non modifiable (pré-rempli) |
| **Avec variantes** | Dropdown avec les tags disponibles (N, S, NO, SE…) | Sélection d'une variante |

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
| **Ajouter un parcours** | Ajoute une nouvelle colonne (numérotée automatiquement) |
| **Supprimer un parcours** | Bouton ✗ en haut de la colonne |
| **Sélectionner une variante** | Dropdown dans chaque cellule à variantes |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Règles métier

- Chaque parcours doit avoir **exactement une variante** sélectionnée par numéro de balise
- Les balises `unique` sont automatiquement pré-remplies et non modifiables
- Les lignes (numéros de balises) sont déterminées par le registre — non modifiables ici
- Un parcours ne peut pas être vide (toutes les variantes doivent être sélectionnées)
- Typiquement 4 à 6 parcours par probatoire
