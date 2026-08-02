# Vue Suivi (Encadrants)

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.3](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Surveiller en temps réel l'avancement de tous les concurrents pendant l'épreuve. Permettre aux encadrants d'intervenir sur les données d'un concurrent (codes, abandon, tracker).

---

## 2. Accès

Encadrants uniquement (tous les mêmes droits).

---

## 3. Structure de l'écran

### 3.1 En-tête (sticky)

- 🕐 **Horloge temps réel** — gros format, toujours visible en haut de l'écran

### 3.2 Liste des concurrents

Liste de tous les concurrents, triée par **ordre de départ** (horaire de départ prévu croissant). Une carte par concurrent.

#### Structure d'une ligne concurrent

```
┌──────────────────────────────────────────────────────────────┐
│  Dupont Marie       PH2   01:12:34     📡               [v]  │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Détail |
|---------|--------|
| Nom / Prénom | Identité du concurrent |
| PH en cours | PH1, PH2, PH3, … PHn (la porte horaire vers laquelle le concurrent progresse), ou **"Arrivé"/"Arrivée"** (accordé selon le sexe du concurrent) quand toutes les PH sont passées. Le numéro de PH est calculé dynamiquement selon l'ordre des balises PH dans le parcours. Une PH est considérée comme passée dès qu'un **horaire de passage** est enregistré sur la balise PH correspondante (indépendamment du code saisi). Cette règle s'applique uniquement à la vue Suivi (la vue Résultats applique ses propres critères de validation). |
| Temps écoulé section | Temps écoulé depuis la dernière PH passée (ou depuis le départ si aucune PH passée). Format **HH:MM:SS**, mis à jour en temps réel |
| Indicateur tracker | 📡 affiché uniquement si le concurrent a un tracker prêté |
| Bouton **"v"** (dépliant) | Ouvre le détail du concurrent |

#### Code couleur des lignes

| Couleur de fond | Signification |
|-----------------|---------------|
| ⚪ Aucun fond | Dans les temps (temps écoulé < temps max de la PH en cours) |
| 🔴 Rouge | En retard sur sa porte horaire (temps écoulé > temps max) |
| 🔘 Grisé | Arrivé + tracker rendu |
| 🟣 Violet clair | DNS ou abandon. Les DNS sont en plus **texte barré** (pour les différencier des abandons qui nécessitent encore un suivi) |

---

## 4. Contenu dépliant (clic sur un concurrent)

Au clic sur la ligne d'un concurrent, un panneau se déplie avec les sections suivantes :

### 4.1 Informations générales

- **Numéro de téléphone** affiché en clair, **cliquable** (copie dans le presse-papier) + bouton **📞** (ouvre l'application d'appel)
- **Parcours** : "Parcours : X"

### 4.2 Tableau des portes horaires

Tableau de N lignes (PH1, PH2, … PHn — autant que de balises PH dans le parcours du concurrent) :

| Colonne | Contenu |
|---------|---------|
| **PH** | PH1 / PH2 / … / PHn (numéro calculé dynamiquement) |
| **Tps min** | Borne inférieure de la section au format **HHhMM** (ex : `0h45`, `1h30`), ou "—" si pas de borne min |
| **Tps max** | Borne supérieure de la section au format **HHhMM** |
| **Tps écoulé** | Temps écoulé sur cette section au format **HHhMM** (temps réel, mis à jour en continu pour la section en cours) |

**Couleurs et états :**

| État de la ligne PH | Fond | Couleur du temps écoulé |
|----------------------|------|-------------------------|
| PH déjà passée (validée) | Fond gris | Couleur selon le résultat (noir/vert/rouge) |
| PH en cours | Fond normal | Voir ci-dessous |
| PH future | Fond normal | `---` (pas encore de temps) |

**Couleur du temps écoulé :**

| Couleur | Condition |
|---------|-----------|
| Noir | Temps < borne min (normal, le candidat est en avance) |
| Vert | Borne min ≤ temps ≤ borne max (dans les temps) |
| Rouge | Temps > borne max (en retard) |

### 4.3 Liste des balises

Tableau détaillé de toutes les balises du parcours du concurrent :

| Colonne | Contenu |
|---------|---------|
| **N°** | Numéro de la balise (1, 2, 3…) |
| **PH** | "PH1", "PH2", etc. si c'est une porte horaire (numéro calculé dynamiquement selon l'ordre dans le parcours), sinon vide |
| **Code renseigné** | Input éditable (2 lettres), pré-rempli avec le code saisi par le stagiaire ou `--` si non renseigné |
| **Code valide ?** | ✅ ou ❌ (comparaison avec le code attendu, ou `--` si code attendu pas encore attribué) |
| **Horaire de passage** | Input éditable (HH:MM:SS), pré-rempli avec l'heure de la saisie du code, ou vide |
| **Bouton ⏱** | Remplit le champ "Horaire de passage" avec l'heure courante (HH:MM:SS) |
| **Bouton ✓** | Enregistre les modifications de cette ligne (code + horaire) |

Les champs **code** et **horaire de passage** sont directement modifiables dans le tableau (inputs in-place, pas de mode lecture/écriture séparé).

#### Balises PH — Affichage en 2 lignes

Pour chaque balise PH, le tableau affiche **2 lignes** au lieu d'une :

| Ligne | Fond | Contenu |
|-------|------|---------|
| **Ligne arrivée** | 🟠 Orange très léger | Heure d'**arrivée** à la PH (étape 1 du mécanisme PH). Colonnes : N°, PH, pas de code (`—`), Code valide = `—`, horaire d'arrivée, bouton ⏱, bouton ✓ |
| **Ligne départ** | 🟢 Vert léger | Heure de **départ/validation** de la PH (étape 2). Colonnes normales : N°, PH, code renseigné, code valide, horaire de validation, bouton ⏱, bouton ✓ |

- La **ligne arrivée** n'a pas de champ code (seul l'horaire est pertinent — correspond au log `ph_arrival`)
- La **ligne départ** contient le code de la balise PH + l'horaire de validation/départ (correspond au log `checkpoint` ou `checkpoint_edit`)
- Chaque ligne dispose de son propre bouton ✓ et peut être enregistrée indépendamment

**Exception — Dernière PH du parcours :**
- La dernière PH (la plus haute séquence parmi les balises PH du concurrent) représente l'**arrivée** : le concurrent ne repart pas de ce point.
- Elle est affichée sur **une seule ligne de validation** (pas de ligne arrivée séparée) :
  - Fond vert léger (comme une ligne départ/validation)
  - Colonnes normales : N°, PH (ex: "PH3"), code renseigné, code valide, horaire de passage, bouton ⏱, bouton ✓
- Le code et l'horaire sont saisis comme pour les autres PH — la section est validée de la même manière

**Bouton ✓ par ligne :**
- Chaque ligne dispose d'un bouton ✓ qui enregistre individuellement les modifications de cette balise (code + horaire)
- Le bouton est actif uniquement si la ligne a été modifiée par rapport à l'état serveur
- L'horaire enregistré est celui du champ "Horaire de passage" (saisi manuellement ou via le bouton ⏱), pas l'heure système au moment du clic
- Les champs **code** et **horaire de passage** sont indépendants : un code peut être enregistré sans horaire, et un horaire peut être enregistré sans code
- Un **code peut être effacé** (champ vidé) : l'enregistrement envoie alors un code `null`, supprimant le code précédemment saisi
- Chaque enregistrement génère une entrée `checkpoint_edit` dans l'historique (§4.6)
- Appuyer sur **Entrée** dans un champ code ou horaire déclenche l'enregistrement de la ligne (équivalent au bouton ✓)

**Bouton ✗ (Annuler) par ligne :**
- À côté du bouton ✓, un bouton **✗** (croix) permet d'annuler les modifications locales et de revenir aux valeurs serveur
- Le bouton est visible et actif uniquement si la ligne a été modifiée par rapport à l'état serveur (même condition que le bouton ✓)
- Au clic : les champs code et horaire sont remis à la dernière valeur connue du serveur

### 4.4 Bouton Abandon

- **"Abandonner"** : marque le concurrent comme ayant abandonné
  - Champ **commentaire obligatoire** expliquant la raison
  - Enregistre l'horodatage de l'abandon
- Si déjà en abandon : le bouton devient **"Annuler l'abandon"**
  - Champ commentaire obligatoire
  - Remet le concurrent dans son état précédent

### 4.5 Bouton Tracker

- **"Tracker rendu"** : confirme la restitution du tracker
  - Demande le **numéro du tracker** rendu (vérification de cohérence avec le n° prêté)
  - Valide la restitution → débloque l'accès aux résultats côté stagiaire
- Si déjà marqué rendu : le bouton devient **"Annuler le rendu"**
  - Annule la validation de restitution → re-bloque l'accès résultats côté stagiaire

### 4.6 Historique des modifications

Liste chronologique de toutes les actions effectuées par les encadrants sur ce concurrent :

| Type d'action | Informations affichées |
|---------------|------------------------|
| Modification code/horaire balise | `Balise XX → "CB" \| HH:MM:SS` (code + heure de passage) |
| Abandon | Commentaire associé |
| Annulation abandon | Commentaire associé |
| Tracker rendu | N° du tracker |
| Annulation rendu tracker | — |

Chaque ligne affiche :
- **À gauche** : l'heure de l'action (`creation_time`, en gris)
- **Au centre** : le **nom de l'auteur** (pseudo ou prénom, en gris)
- **À droite** : la description de l'action

Pour chaque entrée : **infobulle** au survol/clic affichant :
- Heure de l'action (`received_at`)
- Nom de l'encadrant qui a effectué l'action

> 💡 La réponse API `/tracking` inclut un champ `authors` (dictionnaire `author_id → nom_affiché`) pour permettre au frontend de résoudre les noms sans appel supplémentaire.

---

## 5. Récapitulatif (bas de page)

Compteurs synthétiques affichés en bas de la liste des concurrents :

| Compteur | Description |
|----------|-------------|
| Partis | Nombre de concurrents dont le départ a été confirmé |
| En course | Nombre de concurrents encore en course (inscrits − DNS − abandons − arrivés) |
| En section 1 / 2 / … / N | Nombre de concurrents dans chaque section (N = nombre de PH du parcours) |
| Arrivés | Nombre de concurrents ayant franchi la dernière PH |
| DNS | Nombre de non-présentés |
| Abandons | Nombre d'abandons |

---

## 6. Données enregistrées

| Donnée | Moment |
|--------|--------|
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
| **Départ** | Fournit l'heure de départ réelle (début chrono section 1) |
| **Vue publique édition balises** | Reçoit les éditions publiques de codes balises et PH (logs avec `author_id = "public"`) |
| **Résultats** | Utilise les mêmes données pour calculer validé/non validé |
