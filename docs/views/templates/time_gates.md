# Template — Onglet Temps PH

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1 — Parcours / Temps PH](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Définir les temps min/max par porte horaire pour chaque parcours, différenciés hommes/femmes. Ces temps servent de référence et peuvent être surchargés au niveau de chaque événement.

---

## 2. Pré-requis

Les [parcours](courses.md) doivent être créés. Si aucun parcours n'existe, l'onglet affiche un message invitant à les créer d'abord.

---

## 3. Structure de l'écran

### 3.1 Un tableau par parcours

Pour chaque parcours, un tableau affiche les PH avec leurs temps. Le nombre de lignes correspond au **nombre de balises PH** dans le parcours (calculé dynamiquement depuis le registre des balises et la composition du parcours) :

| PH | Temps min (H) | Temps max (H) | Temps min (F) | Temps max (F) |
|----|---------------|---------------|---------------|---------------|
| PH1 | [    ] min | [    ] min | [    ] min | [    ] min |
| PH2 | [    ] min | [    ] min | [    ] min | [    ] min |
| ... | ... | ... | ... | ... |
| PHn | [    ] min | [    ] min | [    ] min | [    ] min |

### 3.2 Wireframe

```
╔═══════════════════════════════════════════════════════════╗
║  Parcours A                                               ║
╠═════╦═══════════╦═══════════╦═══════════╦═══════════╗     ║
║ PH  ║ Min (H)   ║ Max (H)   ║ Min (F)   ║ Max (F)   ║     ║
╠═════╬═══════════╬═══════════╬═══════════╬═══════════╣     ║
║ PH1 ║ [  45  ]  ║ [ 1h15 ]  ║ [  45  ]  ║ [ 1h25 ]  ║     ║
║ PH2 ║ [  30  ]  ║ [ 1h00 ]  ║ [  30  ]  ║ [ 1h10 ]  ║     ║
║ PH3 ║ [  —   ]  ║ [  45  ]  ║ [  —   ]  ║ [  55  ]  ║     ║
║ ... ║ ...       ║ ...       ║ ...       ║ ...       ║     ║
╠═════╩═══════════╩═══════════╩═══════════╩═══════════╝     ║
╚═══════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║  Parcours B                                               ║
║  ...                                                      ║
╚═══════════════════════════════════════════════════════════╝

                              [ Enregistrer ]
```

---

## 4. Actions

| Action | Description |
|--------|-------------|
| **Modifier** | Tous les champs sont éditables directement |
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |

---

## 5. Règles métier

- Les temps sont en **minutes** (saisie libre, affichage converti en h:mm si souhaité)
- Le temps est **par section** (pas cumulatif depuis le départ)
- **Temps min** peut être `null` pour n'importe quelle section (à la discrétion de l'organisateur) — affiché comme `—`
- **Temps max** est toujours obligatoire
- Les temps sont **différenciés H/F** (les femmes ont plus de temps)
- Le nombre de lignes dans le tableau est **dynamique** : il correspond au nombre de balises PH dans le parcours
- Ces temps servent de **référence** : ils peuvent être surchargés pour un événement spécifique (voir [event_time_gates.md](../events/time_gates.md))

### Formules de référence (indicatives)

> ⚠️ Ces formules servent de base de calcul à l'organisation pour les probatoires blancs standards. Les temps saisis dans l'app peuvent différer et ne sont pas contraints par ces formules.

