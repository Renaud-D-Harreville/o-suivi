# Vue Publique — Édition des balises

> **Statut** : Brouillon  
> **Référence** : [Vue publique résultats](public_results.md), [Vue suivi §4.3](suivi.md)

---

## 1. Objectif

Permettre l'édition des codes balises et horaires de passage d'un concurrent, via une page dédiée accessible publiquement.

---

## 2. Accès

- URL : `/events/{uuid}/competitor/{userId}/beacons`
- **Aucune authentification** requise
- Accessible depuis le lien "✏️ Éditer les balises" dans le dépliant de la [vue publique résultats](public_results.md)
- **Tout visiteur** ayant le lien peut éditer les balises de ce concurrent

---

## 3. Structure de l'écran

### 3.1 En-tête

| Élément | Détail |
|---------|--------|
| **Lien retour** | **"Retour aux résultats"** — retour vers la vue résultats publique (`/events/{uuid}`) |
| **Nom de l'événement** | Affiché en haut |
| **Nom du concurrent** | Prénom + Nom du concurrent dont on édite les balises |

### 3.2 Tableau des balises

Tableau inspiré de la vue Suivi ([suivi.md §4.3](suivi.md)), avec les différences suivantes :
- **Pas de colonne "Code valide ?"** (le stagiaire ne doit pas savoir si ses codes sont corrects ou non)
- **Lignes spéciales pour les balises PH** (voir §3.3)

| Colonne | Contenu |
|---------|---------|
| **N°** | Numéro de la balise (1, 2, 3…) |
| **PH** | "PH1", "PH2", etc. si c'est une porte horaire (numéro calculé dynamiquement), sinon vide |
| **Code renseigné** | Input éditable (2 lettres), pré-rempli avec le code saisi ou `--` si non renseigné |
| **Horaire de passage** | Input éditable (HH:MM:SS), pré-rempli avec l'heure de la saisie du code, ou vide |
| **Bouton ⏱** | Remplit le champ "Horaire de passage" avec l'heure courante (HH:MM:SS) |
| **Bouton ✓** | Enregistre les modifications de cette ligne (code + horaire) |

### 3.3 Balises PH — Affichage en 2 lignes

Pour chaque balise PH, le tableau affiche **2 lignes** au lieu d'une :

| Ligne | Fond | Contenu |
|-------|------|---------|
| **Ligne arrivée** | 🟠 Orange très léger | Heure d'**arrivée** à la PH (étape 1 du mécanisme PH). Même colonnes que le tableau standard : N°, PH, pas de code, horaire d'arrivée, bouton ⏱, bouton ✓ |
| **Ligne départ** | 🟢 Vert léger | Heure de **départ/validation** de la PH (étape 2). Colonnes : N°, PH, code renseigné, horaire de validation, bouton ⏱, bouton ✓ |

> 💡 La ligne arrivée n'a pas de champ code (seul l'horaire est pertinent). La ligne départ contient le code de la balise PH + l'horaire de validation/départ. Ce mécanisme à 2 lignes est identique à celui de la vue Suivi encadrants ([suivi.md §4.3](suivi.md)), à l'exception de la colonne "Code valide ?" qui n'est pas affichée ici.

**Exception — Dernière PH du parcours :**
- La dernière PH (la plus haute séquence parmi les balises PH du concurrent) représente l'**arrivée** : le concurrent ne repart pas de ce point.
- Elle est affichée sur **une seule ligne de validation** (pas de ligne arrivée séparée) :
  - Fond vert léger (comme une ligne départ/validation)
  - Colonnes normales : N°, PH (ex: "PH3"), code renseigné, horaire de passage, bouton ⏱, bouton ✓
- Le code et l'horaire sont saisis comme pour les autres PH — la section est validée de la même manière

---

## 4. Règles d'édition

Identiques à [suivi.md §4.3](suivi.md) :

- Les champs **code** et **horaire de passage** sont directement modifiables (inputs in-place)
- Le bouton ✓ est actif uniquement si la ligne a été modifiée
- L'horaire enregistré est celui du champ (saisi manuellement ou via ⏱), pas l'heure système au moment du clic
- Les champs code et horaire sont indépendants : un code peut être enregistré sans horaire, et vice versa
- Un code peut être effacé (champ vidé) → envoie `null`, supprimant le code précédemment saisi
- Appuyer sur **Entrée** dans un champ déclenche l'enregistrement de la ligne

---

## 5. Traçabilité

- Chaque enregistrement génère une entrée **`checkpoint_edit`** dans le log du concurrent
- Le champ `author_id` est fixé à **`"public"`** (identifie que l'édition vient de la page publique, pas d'un encadrant authentifié)
- Ces entrées apparaissent dans l'historique des modifications visible par les encadrants (vue Suivi §4.6)

---

## 6. Données utilisées

| Donnée | Source | Mode |
|--------|--------|------|
| Liste des balises du parcours | Configuration événement (parcours du concurrent) | Lecture |
| Codes saisis + horaires | Logs du concurrent (état reconstruit) | Lecture |
| Heures d'arrivée / validation PH | Logs du concurrent (état reconstruit) | Lecture |
| Modification code/horaire | Entrée `checkpoint_edit` ajoutée au log | Écriture |

---

## 7. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Vue publique résultats** | Page parente — lien retour |
| **Vue Suivi (encadrants)** | Même tableau d'édition, mêmes logs générés — les modifications publiques apparaissent dans l'historique encadrant |

