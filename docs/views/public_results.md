# Vue Publique — Résultats

> **Statut** : Brouillon  
> **Référence** : [Cahier des charges §5.6](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Permettre à quiconque disposant du lien de l'événement de consulter les résultats de tous les concurrents, et d'accéder à l'édition des balises de chaque concurrent.

---

## 2. Accès

- URL publique : `/events/{uuid}`
- **Aucune authentification** requise — toute personne ayant le lien y accède
- Accessible **à tout moment** (pas de restriction temporelle liée à l'avancement de l'épreuve)
- Le lien est partagé par les organisateurs aux stagiaires (par message, email, etc.)

---

## 3. Structure de l'écran

### 3.1 En-tête

- **Nom de l'événement** affiché en haut de page
- **Lien conditionnel "← Vue encadrant"** : affiché **uniquement** si un token JWT valide (rôle `organizer`, non expiré) est présent en localStorage. Pointe vers `/admin/events/{uuid}/resultats`. Discret (petit lien en haut à droite du header).
- **Lien "⏱ Temps intermédiaires"** : lien vers la page de comparaison des splits (`/events/{uuid}/splits`). Toujours affiché. Voir [public_split_times.md](public_split_times.md)
- **Lien "📅 Horaires"** : lien vers la page des horaires (`/events/{uuid}/schedule`). Toujours affiché. Voir [public_schedule.md](public_schedule.md)
- **Lien Routechoices** : affiché **uniquement** si les **2 conditions** suivantes sont remplies :
  1. Le champ `public_routechoices_time` est **renseigné** dans la configuration de l'événement (non null)
  2. L'heure actuelle est **postérieure** à l'heure configurée (combinée avec la date de l'événement)
- Si l'une des conditions n'est pas remplie, le lien n'est pas affiché

### 3.2 Liste des concurrents

Liste triée par **ordre d'arrivée** (premiers arrivés en haut), DNS en fin de liste.

#### Concurrent arrivé (ou abandon / DNS)

Un concurrent est considéré comme **arrivé** dès lors qu'il a franchi la dernière PH, ou qu'il est en **abandon** ou **DNS**.

- Ligne unique : Prénom N. (initiale du nom + point) · **"Arrivé"** (homme) ou **"Arrivée"** (femme) — texte neutre, pas d'indicateur de validation
- Mêmes cas particuliers que la vue suivi (DNS grisé/barré/non cliquable, Abandon badge affiché)

> 💡 La vue publique ne montre **aucun indicateur de validation** (ni ✅ ni ❌) dans la liste. Le stagiaire doit ouvrir le détail pour voir ses résultats détaillés.
> 💡 **Anonymisation** : toutes les vues publiques affichent "Prénom N." (première lettre du nom de famille + point) au lieu du nom complet.

#### Concurrent non arrivé (encore en course)

- Ligne unique : Prénom N. · ⏳ (sablier — pas encore arrivé)

---

## 4. Vue détaillée (dépliable, clic sur une ligne)

Au clic sur la ligne d'un concurrent, un panneau se déplie. Le contenu dépend du statut du concurrent.

### 4.1 Lien vers l'édition des balises

**Toujours affiché en premier** dans le dépliant (que le concurrent soit arrivé ou non) :
- Lien cliquable : **"✏️ Éditer les balises"**
- Redirige vers la page dédiée : `/events/{uuid}/competitor/{userId}/beacons`
- Voir [public_beacon_edit.md](public_beacon_edit.md) pour la spécification complète

### 4.2 Résultats non accessibles — message d'attente

Les résultats d'un concurrent sont **masqués** tant que l'une des conditions suivantes est vraie :
- Le concurrent n'est **pas encore arrivé** (ni abandon, ni DNS)
- Le concurrent a emprunté un **tracker** qui n'a **pas encore été rendu**

Sous le lien d'édition des balises, un texte informatif :
- Ligne 1 : **"Résultats accessibles après l'arrivée du concurrent."**
- Ligne 2 (conditionnelle — uniquement si le concurrent a un tracker) : **"Le tracker doit également être rendu."** — affichée en **violet**

Aucune autre information affichée (pas de §4.3, §4.4, §4.5).

### 4.3 Informations générales (concurrent arrivé uniquement)

Identique à la vue résultats admin (supprimée, fonctionnalité conservée dans les vues publiques) :
- Poids du sac (Départ / Arrivée)
- Heure de départ réelle
- Heure d'arrivée

### 4.4 Résumé par section (concurrent arrivé uniquement)

Tableau récapitulatif par section :

| Colonne | Contenu |
|---------|---------|
| **Section** | Nom de la PH (PH1, PH2…) |
| **Codes** | ✅ si tous les codes de la section sont corrects, ❌ sinon. Basé sur le champ `codes_valid` (indépendant du respect des temps) |
| **Retard** | Retard par PH |
| **Temps section** | Temps officiel de la section |
| **Temps course** | Temps de course effectif (hors pauses) |
| **Pause** | Temps de pause |

### 4.5 Liste détaillée des balises (concurrent arrivé uniquement)

Contenu identique :
- N°, code saisi, validité, temps intermédiaire, cumulé section

---

## 5. Critères de validation

Mêmes règles de validation globale et par section que l'ancienne vue résultats admin :

### 5.1 Validation globale

Un concurrent est **VALIDÉ** si et seulement si **toutes ses sections sont validées**.

### 5.2 Validation par section (PH)

Une section est **validée** (✅) si :

1. La PH est passée dans les temps (borne max obligatoire ; borne min si définie par l'organisateur)
2. Toutes les balises **de cette section** ont été validées (code correct)
3. Les balises de la section sont validées **dans le bon ordre**
4. Uniquement les balises de cette section (pas de balise d'un autre parcours)

---

## 6. Données utilisées (en lecture)

Données utilisées :

| Donnée | Source |
|--------|--------|
| `public_routechoices_time` | Configuration événement (onglet Général) — heure d'affichage public du lien Routechoices |
| Statut d'arrivée de chaque concurrent | Logs (état reconstruit : dernière PH franchie, abandon, DNS) |
| Tracker emprunté (`has_tracker`) | Configuration événement (inscription : `tracker_number` ≠ null) |
| Tracker rendu (`tracker_returned`) | Logs (état reconstruit : log `tracker_returned` / `tracker_returned_cancel`) |

---

## 7. Lien avec les autres vues

| Vue | Interaction |
|-----|-------------|
| **Résultats encadrants** | Même données, même affichage. La vue publique ajoute le lien vers l'édition balises |
| **Édition balises publique** | Lien dans le dépliant de chaque concurrent |
| **Comparaison splits publique** | Lien dans l'en-tête vers `/events/{uuid}/splits` |
| **Configuration** | Fournit les bornes PH, les codes attendus et le lien Routechoices |

