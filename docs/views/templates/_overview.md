# Template de Probatoire — Vue d'ensemble

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.1](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Créer et éditer un modèle de probatoire réutilisable. Un template définit le registre des balises, les parcours et les temps PH. Il sert de base à la création d'événements.

---

## 2. Accès

Encadrants uniquement. Accessible depuis la [page d'accueil admin](../admin_home.md) (onglet Templates).

---

## 3. Structure de l'écran

### 3.1 En-tête

- **Nom du template** (affiché, modifiable inline)

### 3.2 Navigation par onglets (3 onglets)

```
┌────────────────────┬──────────────┬──────────────────┐
│  REGISTRE BALISES  │   PARCOURS   │   TEMPS PH       │
└────────────────────┴──────────────┴──────────────────┘
```

| Onglet | Fichier | Description |
|--------|---------|-------------|
| Registre balises | [beacons.md](beacons.md) | Tableau de toutes les balises du probatoire (registre "tous postes") |
| Parcours | [courses.md](courses.md) | Construction des parcours à partir du registre |
| Temps PH | [time_gates.md](time_gates.md) | Temps min/max par PH par parcours (H/F) |

---

## 4. Ordre de saisie

Les onglets suivent un ordre logique de saisie :
1. **Registre balises** en premier (base de tout)
2. **Parcours** ensuite (sélection des variantes)
3. **Temps PH** en dernier (nécessite les parcours)

> 💡 L'utilisateur peut naviguer librement entre les onglets, mais les parcours ne peuvent être construits que si le registre est rempli, et les temps PH que si les parcours existent.

