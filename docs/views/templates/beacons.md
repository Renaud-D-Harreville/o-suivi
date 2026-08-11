# Template — Onglet Registre des Balises

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1 — Registre "tous postes"](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Saisir l'ensemble des balises positionnées en forêt pour ce probatoire. Ce registre constitue la base à partir de laquelle les parcours sont construits.

---

## 2. Structure de l'écran

### 2.1 Tableau des balises

Tableau entièrement modifiable, une ligne par balise :

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| **N°** | int | Numéro d'ordre (1, 2, 3…). Les parcours suivent cet ordre | ✅ |
| **ID** | int | Identifiant technique unique (≥ 31), auto-attribué par le frontend. Non modifiable | Auto |
| **Tag** | dropdown | `unique` / `N` / `E` / `S` / `O` / `NO` / `NE` / `SE` / `SO` | ✅ |
| **PH** | checkbox | Coché si la balise est une porte horaire | ✅ |
| **Coordonnées** | texte | Latitude, longitude (ex: "45.883424, 5.863804") | ❌ |
| **Section** | auto | Déduite des PH : les balises entre deux PH appartiennent à la même section. Le numéro de section est calculé dynamiquement selon l'ordre des balises PH dans chaque parcours | Auto |

> 💡 La dernière balise PH = arrivée. Le nombre de PH est variable selon les besoins de l'organisateur.

> 💡 Les balises avec `tag = unique` sont communes à tous les parcours. Les balises avec un tag directionnel existent en variantes : un même numéro peut avoir plusieurs lignes (ex : 5-NO, 5-SE).

### 2.2 Wireframe

```
┌─────┬─────┬──────────┬──────┬────────────────────────┬───────────┐
│ N°  │ ID  │   Tag    │  PH  │     Coordonnées        │  Section  │
├─────┼─────┼──────────┼──────┼────────────────────────┼───────────┤
│  1  │ 31  │ unique   │  ☐  │ 45.883424, 5.863804    │ Section 1 │
│  2  │ 32  │ NO       │  ☐  │                        │ Section 1 │
│  2  │ 33  │ SE       │  ☐  │                        │ Section 1 │
│  3  │ 34  │ unique   │  ☑  │ 45.892112, 5.871256    │ Section 1 │  ← Fin section 1 (= PH1)
│  4  │ 35  │ N        │  ☐  │ 45.905000, 5.865000    │ Section 2 │
│  4  │ 36  │ S        │  ☐  │                        │ Section 2 │
│  5  │ 37  │ unique   │  ☐  │ 45.918000, 5.878000    │ Section 2 │
│  6  │ 38  │ unique   │  ☑  │ 45.930000, 5.885000    │ Section 2 │  ← Fin section 2 (= PH2)
│ ... │ ... │ ...      │ ...  │ ...                    │ ...       │
│ 18  │ 52  │ unique   │  ☑  │ 45.945000, 5.890000    │ Section N │  ← Arrivée (= dernière PH)
├─────┴─────┴──────────┴──────┴────────────────────────┴───────────┤
│  [ + Ajouter une balise ]                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Actions

| Action | Description |
|--------|-------------|
| **Ajouter** | Nouvelle ligne vide en bas du tableau |
| **Supprimer** | Bouton ✗ sur chaque ligne (avec confirmation) |
| **Modifier** | Tous les champs sont éditables directement dans le tableau |
| **Enregistrer** | Bouton en bas de page — sauvegarde en BDD sans quitter la page |

---

## 4. Règles métier

- Un même **numéro** peut apparaître plusieurs fois (variantes avec tags différents)
- Les balises avec `tag = unique` ne peuvent apparaître qu'**une seule fois** par numéro
- Les PH sont toujours sur des balises `unique`
- La **section** est déduite automatiquement : toutes les balises entre deux PH (ou avant la 1ère PH) appartiennent à la même section
- Le nombre de sections est **variable** (= nombre de balises PH du parcours)
- Le numéro de PH (PH1, PH2, ...) est calculé dynamiquement selon l'ordre d'apparition dans chaque parcours

