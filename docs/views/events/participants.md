# Événement — Onglet Participants

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.2](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Gérer la liste des concurrents inscrits à l'événement : import, ajout, modification, suppression.

---

## 2. Structure de l'écran

### 2.1 Tableau des participants

Tableau entièrement modifiable, une ligne par participant :

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| **Nom** | texte | Nom de famille | ✅ |
| **Prénom** | texte | Prénom | ✅ |
| **Sexe** | dropdown | `H` / `F` | ✅ |
| **Téléphone** | texte | Numéro de téléphone | ✅ |
| **ID Routechoices** | texte | Identifiant Routechoices (clé de déduplication prioritaire) | ❌ |

### 2.2 Wireframe

```
┌───────────┬──────────┬──────┬────────────────┬─────────────────┬──────┐
│ Nom       │ Prénom   │ Sexe │ Téléphone      │ ID Routechoices │      │
├───────────┼──────────┼──────┼────────────────┼─────────────────┼──────┤
│ Dupont    │ Marie    │  F   │ 06 12 34 56 78 │ rc_12345        │ [✗] │
│ Martin    │ Pierre   │  H   │ 06 98 76 54 32 │                 │ [✗] │
│ Leroy     │ Julie    │  F   │ 06 11 22 33 44 │ rc_67890        │ [✗] │
│ Bernard   │ Thomas   │  H   │ 06 55 66 77 88 │                 │ [✗] │
└───────────┴──────────┴──────┴────────────────┴─────────────────┴──────┘

[ + Ajouter un participant ]  [ Importer CSV ]       [ Enregistrer ]
```

---

## 3. Actions

| Action | Description |
|--------|-------------|
| **Importer CSV** | Import d'un fichier CSV avec les colonnes Nom, Prénom, Sexe, Téléphone, ID Routechoices. Déduplique via routechoices_id puis nom+prénom. Crée les utilisateurs en BDD s'ils n'existent pas, puis les inscrit à l'événement |
| **Ajouter** | Bouton « + Ajouter un participant » qui insère une ligne vide éditable en bas du tableau |
| **Modifier** | Tous les champs sont éditables directement dans le tableau |
| **Supprimer** | Bouton ✗ sur chaque ligne (avec confirmation) — désinscrit le participant de l'événement |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 4. Import CSV

- Colonnes attendues : `Nom`, `Prénom`, `Sexe`, `Téléphone`, `ID Routechoices`
- Toutes les colonnes sont obligatoires dans le fichier — si une colonne est absente, afficher un message d'erreur
- **Séparateur** : auto-détection `;` ou `,` (basé sur la première ligne)
- **Encodage** : UTF-8
- **Parsing** : côté client (pas de nouvel endpoint backend)
- **Merge** : les entrées importées sont fusionnées avec le tableau existant (pas de remplacement)
- **Déduplication locale** : par `routechoices_id` en priorité, puis par `nom + prénom` en fallback. Si doublon détecté, l'entrée existante est mise à jour avec les données du CSV
- Si un utilisateur avec le même identifiant existe déjà en BDD, il est réutilisé (pas de doublon)
- Si l'utilisateur n'existe pas, il est créé automatiquement (à la sauvegarde)
- Après import, les participants apparaissent dans le tableau (modifiables). L'utilisateur doit cliquer « Enregistrer » pour persister les changements

---

## 5. Règles métier

- Un participant ne peut être inscrit qu'**une seule fois** par événement
- La suppression **désinscrit** le participant de l'événement, elle ne supprime pas l'utilisateur de la BDD
- Les modifications (nom, prénom, tel, sexe, ID Routechoices) modifient les données de l'**utilisateur** (pas seulement l'inscription)
- Le `routechoices_id` est **unique** parmi tous les utilisateurs : deux utilisateurs ne peuvent pas avoir le même identifiant Routechoices
- **Déduplication** (sauvegarde) : par `routechoices_id` en priorité, puis par `nom + prénom` en fallback

