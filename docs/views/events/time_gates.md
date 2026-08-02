# Événement — Onglet Barrières Horaires

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1 — Ajustement des temps par épreuve](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Visualiser les temps PH de référence (issus du template) et les ajuster si nécessaire pour cet événement spécifique (conditions météo, terrain, etc.).

---

## 2. Pré-requis

Un template de probatoire doit être sélectionné dans l'onglet [Général](general.md), avec des temps PH définis.

---

## 3. Structure de l'écran

### 3.1 Deux tableaux par parcours

Pour chaque parcours, deux tableaux superposés :

**Tableau 1 — Temps de référence** (lecture seule, issus du template) :

| PH | Min (H) | Max (H) | Min (F) | Max (F) |
|----|---------|---------|---------|---------|
| PH1 | 45 min | 1h15 | 45 min | 1h25 |
| PH2 | 30 min | 1h00 | 30 min | 1h10 |
| PH3 | — | 45 min | — | 55 min |
| ... | ... | ... | ... | ... |

**Tableau 2 — Temps ajustés pour cet événement** (modifiable) :

| PH | Min (H) | Max (H) | Min (F) | Max (F) | Diff |
|----|---------|---------|---------|---------|------|
| PH1 | [ 50 ] | [ 1h23 ] | [ 50 ] | [ 1h34 ] | +10% |
| PH2 | [ 32 ] | [ 1h03 ] | [ 32 ] | [ 1h13 ] | +5% |
| PH3 | [ — ] | [ 52 ] | [ — ] | [ 1h04 ] | +15% |
| ... | ... | ... | ... | ... | ... |

> 💡 Le nombre de lignes dans chaque tableau est **dynamique** : il correspond au nombre de balises PH dans le parcours.

### 3.2 Ajustement par pourcentage (en bas de l'écran)

Sous les tableaux, un bloc permet d'ajuster les temps par un pourcentage global par section :

```
┌──────┬────────────────┐
│  PH  │  % ajouté      │
├──────┼────────────────┤
│ PH1  │  [ +10 ] %     │
│ PH2  │  [  +5 ] %     │
│ PH3  │  [ +15 ] %     │
│ ...  │  ...           │
└──────┴────────────────┘

        [ Appliquer les pourcentages ]
```

**Comportement :**
- Un input par PH (nombre dynamique, autant que de PH dans le parcours) permettant de saisir un pourcentage à ajouter aux temps de référence
- Le bouton **"Appliquer les pourcentages"** recalcule les temps ajustés à partir des temps de référence + les pourcentages
- Après application, les temps restent librement modifiables manuellement (l'encadrant peut encore affiner)
- Le pourcentage s'applique **par section** : tous les temps de la PH (min H, max H, min F, max F) sont augmentés du même pourcentage → identique pour hommes et femmes
- Arrondi : **minute inférieure** (`floor`) pour les temps min, **minute supérieure** (`ceil`) pour les temps max (voir §5)

### 3.3 Wireframe complet

```
╔══════════════════════════════════════════════════════════╗
║  Parcours 1                                              ║
║                                                          ║
║  Temps de référence (template) :                         ║
║  ┌─────┬─────────┬─────────┬─────────┬─────────┐         ║
║  │ PH  │ Min (H) │ Max (H) │ Min (F) │ Max (F) │         ║
║  ├─────┼─────────┼─────────┼─────────┼─────────┤         ║
║  │ PH1 │  45     │  1h15   │  45     │  1h25   │         ║
║  │ PH2 │  30     │  1h00   │  30     │  1h10   │         ║
║  │ PH3 │  —      │  45     │  —      │  55     │         ║
║  │ ... │  ...    │  ...    │  ...    │  ...    │         ║
║  └─────┴─────────┴─────────┴─────────┴─────────┘         ║
║                                                          ║
║  Temps ajustés (cet événement) :                         ║
║  ┌─────┬─────────┬─────────┬─────────┬─────────┬──────┐  ║
║  │ PH  │ Min (H) │ Max (H) │ Min (F) │ Max (F) │ Diff │  ║
║  ├─────┼─────────┼─────────┼─────────┼─────────┼──────┤  ║
║  │ PH1 │ [  50 ] │ [1h23 ] │ [  50 ] │ [1h34 ] │ +10% │  ║
║  │ PH2 │ [  32 ] │ [1h03 ] │ [  32 ] │ [1h13 ] │  +5% │  ║
║  │ PH3 │ [  —  ] │ [  52 ] │ [  —  ] │ [1h04 ] │ +15% │  ║
║  │ ... │  ...    │  ...    │  ...    │  ...    │  ... │  ║
║  └─────┴─────────┴─────────┴─────────┴─────────┴──────┘  ║
║                                                          ║
║  [ Réinitialiser depuis le template ]                    ║
╠══════════════════════════════════════════════════════════╣
║  Parcours 2                                              ║
║  ...                                                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  PH1 : [ +10 ] %    PH2 : [ +5 ] %                       ║
║  PH3 : [ +15 ] %    ...                                  ║
║                                                          ║
║              [ Appliquer les pourcentages ]              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

                                              [ Enregistrer ]
```

---

## 4. Actions

| Action | Description |
|--------|-------------|
| **Appliquer les pourcentages** | Recalcule tous les temps ajustés à partir des temps de référence + le % de chaque PH |
| **Modifier manuellement** | Champs éditables dans le tableau "Temps ajustés" (toujours possible, y compris après application des pourcentages) |
| **Réinitialiser** (par parcours) | Recopie les temps du template dans les temps ajustés pour ce parcours (avec confirmation) |
| **Tout réinitialiser** (en bas de page) | Réinitialise les temps ajustés de **tous les parcours** d'un coup et remet les pourcentages à 0 (avec confirmation) |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Calcul des pourcentages

Formule : 
- **Temps min ajusté** = `floor(temps min de référence × (1 + pourcentage / 100))` — arrondi à la **minute inférieure**
- **Temps max ajusté** = `ceil(temps max de référence × (1 + pourcentage / 100))` — arrondi à la **minute supérieure**

- S'applique identiquement à H et F
- Si le temps de référence est `null` (pas de borne min), le temps ajusté reste `null`
- Exemple temps max : 75 min, +10% → 75 × 1.10 = 82.5 → **83 min**
- Exemple temps min : 45 min, +10% → 45 × 1.10 = 49.5 → **49 min**

---

## 6. Colonne "Diff"

> ⚠️ À définir — voir backlog. Le mode de calcul et l'affichage de la différence restent à valider.

---

## 7. Règles métier

- Les temps de référence sont en **lecture seule** (copiés depuis le template, non modifiables ici)
- Les temps ajustés sont initialisés avec les temps de référence à la création de l'événement
- Les ajustements sont **par événement** : ils ne modifient pas le template
- Ce sont les **temps ajustés** qui sont utilisés pendant l'épreuve (vue suivi, résultats, validation PH)
- Les temps restent **modifiables à tout moment**, y compris pendant l'épreuve
- Le bouton **Réinitialiser** remet les temps ajustés aux valeurs du template et les pourcentages à 0
