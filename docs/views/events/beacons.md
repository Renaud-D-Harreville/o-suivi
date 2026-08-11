# Événement — Onglet Balises

> **Statut** : Validé  
> **Référence** : [Cahier des charges §6.2](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Gérer le registre des balises de l'événement (copié du template à la création, mais indépendant ensuite) et attribuer un code 2 lettres unique à chaque balise. 
Permet d'adapter les balises aux conditions du jour (météo, terrain).

---

## 2. Initialisation

Les balises de l'événement sont importées depuis le template via le bouton **"Initialiser depuis le template"** dans l'onglet [Général](general.md). 
À partir de ce moment, le registre de l'événement est **indépendant** du template : les modifications ici n'affectent pas le template, et vice-versa.

---

## 3. Structure de l'écran

### 3.1 Tableau des balises

Tableau entièrement modifiable, une ligne par balise :

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| **N°** | int | Numéro d'ordre (1, 2, 3…) | ✅ |
| **ID** | int | Identifiant technique unique (≥ 31), hérité du template. Non modifiable | Auto |
| **Tag** | dropdown | `unique` / `N` / `E` / `S` / `O` / `NO` / `NE` / `SE` / `SO` | ✅ |
| **PH** | checkbox | Coché si la balise est une porte horaire | ✅ |
| **Code** | texte | 2 lettres majuscules (saisie libre, majuscules auto) | ❌ |
| **Coordonnées** | texte | Latitude, longitude (ex: "45.883424, 5.863804") | ❌ |

### 3.2 Wireframe

```
┌─────┬─────┬────────────┬──────┬────────────┬────────────────────────┬──────┐
│ N°  │ ID  │   Tag      │  PH  │    Code    │     Coordonnées        │      │
├─────┼─────┼────────────┼──────┼────────────┼────────────────────────┼──────┤
│  1  │ 31  │ [▼ unique] │  ☐  │ [ AB ]     │ 45.883424, 5.863804    │ [✗] │
│  2  │ 32  │ [▼ NO   ]  │  ☐  │ [ CD ]     │                        │ [✗] │
│  2  │ 33  │ [▼ SE   ]  │  ☐  │ [ EF ]     │                        │ [✗] │
│  3  │ 34  │ [▼ unique] │  ☑  │ [ GH ]     │ 45.892112, 5.871256    │ [✗] │
│  4  │ 35  │ [▼ N    ]  │  ☐  │ [ IJ ]     │ 45.905000, 5.865000    │ [✗] │
│  4  │ 36  │ [▼ S    ]  │  ☐  │ [ KL ]     │                        │ [✗] │
│  5  │ 37  │ [▼ unique] │  ☐  │ [ MN ]     │ 45.918000, 5.878000    │ [✗] │
│  6  │ 38  │ [▼ unique] │  ☑  │ [ OP ]     │ 45.930000, 5.885000    │ [✗] │
│ ... │ ... │ ...        │ ...  │ ...        │ ...                    │      │
├─────┴─────┴────────────┴──────┴────────────┴────────────────────────┴──────┤
│  [ + Ajouter une balise ]  [ Enregistrer ]                                 │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Actions

| Action | Description |
|--------|-------------|
| **Ajouter** | Nouvelle ligne vide en bas du tableau |
| **Supprimer** | Bouton ✗ sur chaque ligne (avec confirmation) |
| **Modifier** | Tous les champs sont éditables directement (N°, tag, PH, code) |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Règles métier

### Codes
- Chaque code doit être **exactement 2 lettres** (majuscules)
- Chaque code doit être **unique** au sein de l'événement (pas de doublon)
- En cas de doublon, une erreur visuelle est affichée sur les champs concernés
- Les codes peuvent être attribués **tardivement**, y compris après le début de l'épreuve
- Les champs vides sont autorisés (pas encore attribués)
- La saisie est **manuelle** (pas de génération automatique)

### Registre
- Un même numéro peut apparaître plusieurs fois (variantes avec tags différents)
- Les balises avec `tag = unique` ne peuvent apparaître qu'une seule fois par numéro
- Les PH sont toujours sur des balises `unique`
- Le numéro de PH (PH1, PH2, ...) est calculé dynamiquement selon l'ordre de la balise PH dans chaque parcours
- **Modifiable à tout moment**, y compris pendant l'épreuve

> ⚠️ Modifier le registre pendant l'épreuve impacte potentiellement les parcours et les validations en cours. L'encadrant doit en être conscient.
