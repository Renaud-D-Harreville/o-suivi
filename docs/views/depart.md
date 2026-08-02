# Vue Départ (Encadrants)

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.2](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Visualiser et gérer le départ séquentiel des concurrents de manière fluide. L'encadrant confirme manuellement chaque départ via un bouton dédié.

---

## 2. Accès

Encadrants uniquement (tous les mêmes droits).

---

## 3. Structure de l'écran

### 3.1 En-tête (sticky)

- **Header commun de navigation** — boutons Config / Départ / Suivi / Résultats (voir [events/_overview.md §4](events/_overview.md))
- 🕐 **Horloge temps réel** — gros format, affichée sous le header commun, toujours visible même au scroll

### 3.2 Liste des concurrents

Liste complète des concurrents, triée par :
1. Horaire de départ prévu (croissant)
2. Numéro de parcours (1→6) en cas d'égalité d'horaire

#### Structure d'une ligne concurrent (3 sous-lignes)

```
┌─────────────────────────────────────────────────────┐
│  Dupont Marie                                       │  ← Ligne 1 : Nom / Prénom
│  08:32  |  Parcours 3  |  Tracker #12       [+]     │  ← Ligne 2 : Infos + bouton dépliant
│              [ DÉPART ]                             │  ← Ligne 3 : Bouton départ
└─────────────────────────────────────────────────────┘
```

| Sous-ligne | Contenu                                                                         |
|------------|---------------------------------------------------------------------------------|
| Ligne 1 | Nom / Prénom                                                                    |
| Ligne 2 | Horaire de départ · Parcours attribué · Tracker prêté (n° — **affiché uniquement si un tracker est prêté**) · Bouton **"+"** |
| Ligne 3 | Bouton **"Départ"** (centré)                                                    |

#### Contenu dépliant (bouton "+")
zqw, 
Au clic sur "+", un panneau se déplie sous la ligne du concurrent avec les éléments suivants :

**Téléphone :**
- Numéro affiché, **cliquable** (copie dans le presse-papier au clic)
- Bouton **📞** à droite → ouvre l'application d'appel avec le numéro pré-rempli

**Champs modifiables** (5 champs, même pattern pour chacun) :

| Champ | Valeur affichée | Détail |
|-------|-----------------|--------|
| Poids du sac | Nombre (kg) ou vide | Optionnel |
| Horaire de départ (prévu) | HH:MM | Toujours modifiable |
| Heure de départ réelle | HH:MM | Toujours modifiable. Valider ce champ confirme le départ avec l'heure saisie (même effet que le bouton "Départ" mais avec une heure personnalisée). Si le concurrent est déjà parti, met à jour son heure de départ effective. |
| Parcours attribué | Numéro (1 à 6) | Toujours modifiable |
| N° tracker prêté | Numéro ou "—" | `null` si non prêté |

**Pattern d'édition** (identique pour les 5 champs) :
1. Le champ est **grisé** (lecture seule) par défaut
2. Bouton **✏️** (stylo) à droite du champ → dégrise le champ, active l'édition
3. En mode édition, deux boutons apparaissent :
   - **✓** (valider) → enregistre la modification, repasse en lecture seule
   - **✗** (annuler) → annule la saisie, repasse en lecture seule avec la valeur précédente

**Actions supplémentaires dans le dépliant :**
- Bouton **"Absent"** → marque le concurrent comme non présenté (DNS)
- Bouton **"Annuler le départ"** → visible uniquement si le concurrent est déjà parti (permet de revenir en arrière)

---

## 4. Code couleur des lignes

| Couleur | Signification | Critère |
|---------|---------------|---------|
| 🔘 Grisé | Concurrent déjà parti | Bouton "Départ" cliqué |
| 🟢 Vert | Prochain(s) à partir | Même horaire de départ que le plus proche non parti |
| 🟠 Orange | Horaire d'après | Horaire de départ immédiatement suivant le vert |
| ⚪ Blanc | En attente | Tous les autres (départ plus tard) |

> 💡 Si plusieurs concurrents partagent le même horaire de départ, ils sont **tous** en vert (ou tous en orange) ensemble.

---

## 5. Comportements

### 5.1 Bouton "Départ"

- Visible sur chaque ligne de concurrent non encore parti
- Au clic : le concurrent passe en **grisé** (parti)
- L'**heure réelle du clic** est enregistrée comme heure de départ effective
- Cette heure sert de référence pour le chrono de la section 1
- Le bouton disparaît une fois le départ confirmé

### 5.2 Annuler un départ

- Bouton **"Annuler le départ"** visible dans le dépliant "+" d'un concurrent déjà parti
- Remet le concurrent dans l'état "non parti" (le bouton "Départ" réapparaît)
- L'heure de départ réelle est effacée

### 5.3 Modification des champs (horaire, parcours, tracker, poids)

- Toujours modifiable, quel que soit l'état du concurrent (non parti, parti, absent)
- La modification de l'horaire recalcule dynamiquement le tri de la liste et les couleurs
- La modification du parcours met à jour l'affichage en ligne 2

### 5.4 Bouton "Absent"

- Accessible via le dépliant "+"
- Marque le concurrent comme **non présenté** (DNS)
- Le concurrent reste visible dans la liste : fond grisé + texte barré
- Le bouton "Départ" est masqué pour un concurrent marqué absent
- Réversible : on peut annuler le statut absent (le concurrent réapparaît normalement)

### 5.5 Liste toujours complète

- Les départs passés sont grisés mais **jamais masqués**
- Permet de vérifier à tout moment qui est parti et quand

---

## 6. Données enregistrées

| Donnée | Moment de l'enregistrement |
|--------|----------------------------|
| Heure de départ réelle | Clic sur "Départ" |
| Statut absent (DNS) | Clic sur "Absent" |
| Poids du sac (départ) | Saisie dans le dépliant |
| N° tracker prêté | Saisie dans le dépliant |
| Parcours attribué | Modifiable dans le dépliant |
| Horaire de départ prévu | Modifiable dans le dépliant |

---

## 7. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Configuration (§5.1.2)** | Fournit : liste des concurrents, horaires de départ, parcours attribués |
| **Suivi (§5.3)** | Reçoit l'heure de départ réelle → démarre le chrono section 1 |
