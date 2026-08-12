# Vue Suivi (Encadrants)

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.2 et §5.3](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Vue unique de gestion des concurrents pendant l'épreuve. Combine la gestion des départs (confirmation, édition des champs d'inscription) et le suivi en temps réel de l'avancement (portes horaires, balises, actions encadrant).

---

## 2. Accès

Encadrants uniquement (tous les mêmes droits).

---

## 3. Structure de l'écran

### 3.1 En-tête (sticky)

- **Header commun de navigation** — boutons Config / Suivi (voir [events/_overview.md §4](events/_overview.md))
- 🕐 **Horloge temps réel** — gros format, affichée sous le header commun, toujours visible même au scroll

### 3.2 Liste des concurrents

Liste de tous les concurrents, triée par **horaire de départ prévu** (croissant), puis par **ordre de départ** en cas d'égalité. Une carte par concurrent.

#### Structure d'une ligne concurrent

```
┌──────────────────────────────────────────────────────────────┐
│  Dupont Marie       PH2   01:12:34     📡   [DÉPART]   [v]  │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Détail |
|---------|--------|
| Nom / Prénom | Identité du concurrent |
| PH en cours | PH1, PH2, … PHn, ou **"Arrivé"/"Arrivée"** (accordé selon le sexe). Le numéro de PH est calculé dynamiquement. Une PH est considérée comme passée dès qu'un **horaire de passage** est enregistré (indépendamment du code saisi) |
| Temps écoulé section | Temps écoulé depuis la dernière PH passée (ou depuis le départ). Format **HH:MM:SS**, mis à jour en temps réel |
| Indicateur tracker | 📡 affiché uniquement si le concurrent a un tracker prêté et non rendu |
| Bouton **"DÉPART"** | Bleu, affiché uniquement si le concurrent n'est pas encore parti et n'est pas DNS. Confirme le départ au clic |
| Label **"Parti à HH:MM"** | Affiché à la place du bouton DÉPART une fois le concurrent parti |
| Bouton **"v"** (dépliant) | Ouvre le détail du concurrent |

#### Code couleur des lignes

Les concurrents non partis utilisent le système de couleur **départ** :

| Couleur | Signification | Critère |
|---------|---------------|---------|
| 🟢 Vert | Prochain(s) à partir | Même horaire de départ que le plus proche non parti |
| 🟠 Orange | Horaire d'après | Horaire de départ immédiatement suivant le vert |
| ⚪ Blanc | En attente | Tous les autres (départ plus tard) |

> 💡 Si plusieurs concurrents partagent le même horaire de départ, ils sont **tous** en vert (ou tous en orange) ensemble.

Les concurrents partis utilisent le système de couleur **suivi** :

| Couleur de fond | Signification |
|-----------------|---------------|
| ⚪ Aucun fond | Dans les temps (temps écoulé < temps max de la PH en cours) |
| 🔴 Rouge | En retard sur sa porte horaire (temps écoulé > temps max) |
| 🔘 Grisé | Arrivé + tracker rendu |
| 🟣 Violet clair | DNS ou abandon. Les DNS sont en plus **texte barré** |

---

## 4. Contenu dépliant (clic sur un concurrent)

Au clic sur la ligne d'un concurrent, un panneau se déplie avec deux zones.

### 4.1 Zone Départ — Informations et édition inscription

Toujours visible. Contient :

**Téléphone :**
- Numéro affiché, **cliquable** (copie dans le presse-papier) + bouton **📞** (ouvre l'application d'appel)

**Champs modifiables** (5 champs, même pattern pour chacun) :

| Champ | Valeur affichée | Détail |
|-------|-----------------|--------|
| Horaire de départ (prévu) | HH:MM | Toujours modifiable |
| Heure de départ réelle | HH:MM | Toujours modifiable. Valider ce champ confirme le départ avec l'heure saisie |
| Parcours attribué | Numéro (1 à 6) | Toujours modifiable |
| N° tracker prêté | Numéro ou "—" | `null` si non prêté |
| Poids du sac | Nombre (kg) ou vide | Optionnel |

**Pattern d'édition** (identique pour les 5 champs) :
1. Le champ est en lecture seule par défaut
2. Bouton **✏️** à droite → active l'édition
3. En mode édition : **✓** (valider) et **✗** (annuler)

**Actions départ :**
- **"Absent"** → marque le concurrent comme non présenté (DNS), commentaire obligatoire
- **"Annuler absent"** → visible si DNS, commentaire obligatoire
- **"Annuler le départ"** → visible si le concurrent est déjà parti

### 4.2 Zone Suivi — Portes horaires, balises, actions (visible uniquement si le concurrent est parti)

#### 4.2.1 Tableau des portes horaires

Tableau de N lignes (PH1, PH2, … PHn) :

| Colonne | Contenu |
|---------|---------|
| **PH** | PH1 / PH2 / … / PHn |
| **Tps min** | Borne inférieure au format **HHhMM**, ou "—" |
| **Tps max** | Borne supérieure au format **HHhMM** |
| **Tps écoulé** | Temps écoulé au format **HHhMM** (temps réel pour la section en cours) |

**Couleurs et états :**

| État de la ligne PH | Fond | Couleur du temps écoulé |
|----------------------|------|-------------------------|
| PH déjà passée | Fond gris | Couleur selon le résultat (noir/vert/rouge) |
| PH en cours | Fond normal | Voir ci-dessous |
| PH future | Fond normal | `---` (pas encore de temps) |

**Couleur du temps écoulé :**

| Couleur | Condition |
|---------|-----------|
| Noir | Temps < borne min |
| Vert | Borne min ≤ temps ≤ borne max |
| Rouge | Temps > borne max |

#### 4.2.2 Liste des balises

Tableau détaillé de toutes les balises du parcours :

| Colonne | Contenu |
|---------|---------|
| **N°** | Numéro de la balise |
| **PH** | "PH1", "PH2", etc. si porte horaire, sinon vide |
| **Code renseigné** | Input éditable (2 lettres) |
| **Code valide ?** | ✅ ou ❌ ou `--` |
| **Horaire de passage** | Input éditable (HH:MM:SS) |
| **Bouton ⏱** | Remplit avec l'heure courante |
| **Bouton ✓** | Enregistre les modifications de cette ligne |

Les balises PH sont affichées en 2 lignes (arrivée orange / départ vert), sauf la dernière PH du parcours (ligne unique de validation).

#### 4.2.3 Bouton Abandon

- **"Abandonner"** : commentaire obligatoire
- **"Annuler l'abandon"** : commentaire obligatoire

#### 4.2.4 Bouton Tracker

- **"Tracker rendu"** : confirme la restitution
- **"Annuler le rendu"** : annule la restitution

#### 4.2.5 Historique des modifications

Liste chronologique de toutes les actions effectuées sur ce concurrent :

| Type d'action | Informations affichées |
|---------------|------------------------|
| Départ | "Départ" |
| Annulation départ | "Annulation départ" |
| Modification départ | Heure modifiée |
| Absent (DNS) | Commentaire associé |
| Annulation absent | Commentaire associé |
| Poids sac | Poids en kg |
| Modification inscription | Champ modifié |
| Modification code/horaire balise | `Balise XX → "CB" \| HH:MM:SS` |
| Abandon | Commentaire associé |
| Annulation abandon | Commentaire associé |
| Tracker rendu | N° du tracker |
| Annulation rendu tracker | — |

Chaque ligne affiche :
- **À gauche** : l'heure de l'action (en gris)
- **Au centre** : le **nom de l'auteur** (en gris)
- **À droite** : la description de l'action

---

## 5. Récapitulatif (bas de page)

Compteurs synthétiques affichés en bas de la liste des concurrents :

| Compteur | Description |
|----------|-------------|
| En attente | Nombre de concurrents ni partis ni DNS |
| Partis | Nombre de concurrents dont le départ a été confirmé |
| En course | Nombre de concurrents encore en course |
| En section 1 / 2 / … / N | Nombre de concurrents dans chaque section |
| Arrivés | Nombre de concurrents ayant franchi la dernière PH |
| DNS | Nombre de non-présentés |
| Abandons | Nombre d'abandons |

---

## 6. Données enregistrées

| Donnée | Moment |
|--------|--------|
| Heure de départ réelle | Clic sur "DÉPART" |
| Statut absent (DNS) | Clic sur "Absent" |
| Poids du sac (départ) | Saisie dans le dépliant |
| N° tracker prêté | Saisie dans le dépliant |
| Parcours attribué | Modifiable dans le dépliant |
| Horaire de départ prévu | Modifiable dans le dépliant |
| Modification code balise | Édition inline + bouton ✓ par ligne |
| Modification horaire passage | Édition inline + bouton ✓ par ligne |
| Abandon + commentaire | Clic "Abandonner" |
| Annulation abandon + commentaire | Clic "Annuler l'abandon" |
| Tracker rendu + n° tracker | Clic "Tracker rendu" |
| Annulation rendu tracker | Clic "Annuler le rendu" |
| Encadrant + horodatage | Pour chaque action ci-dessus |

---

## 7. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Configuration** | Fournit : liste des concurrents, horaires de départ, parcours attribués, bornes PH, codes attendus |
| **Vue publique édition balises** | Reçoit les éditions publiques de codes balises et PH (logs avec `author_id = "public"`) |
| **Vue publique résultats** | Utilise les mêmes données pour calculer validé/non validé |
