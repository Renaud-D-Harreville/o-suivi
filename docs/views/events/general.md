# Événement — Onglet Informations Générales

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1.2](../../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Renseigner les informations de base de l'événement.

---

## 2. Structure de l'écran

### 2.1 Lien public

Tout en haut de l'onglet, un lien cliquable vers la page publique de l'événement :

- URL : `/events/{uuid}` (relative au domaine)
- Affiché en lecture seule
- Permet de copier/partager facilement le lien d'accès public (résultats, édition balises…)

### 2.2 Champs

| Champ | Type | Description | Obligatoire |
|-------|------|-------------|-------------|
| **Nom** | texte | Nom de l'événement | ✅ |
| **Date** | date | Date de l'événement | ✅ |
| **Template de probatoire** | dropdown | Sélection parmi les templates existants | ✅ |
| **Heure du premier départ** | heure (HH:MM) | Heure à laquelle le premier concurrent part | ✅ |
| **Lien Routechoices** | URL | Lien vers l'événement Routechoices (traces GPS) | ❌ |
| **Heure d'affichage Routechoices (public)** | heure (HH:MM) + bouton ⏱ | Heure à partir de laquelle le lien Routechoices est visible sur la page publique des résultats. Bouton ⏱ pour remplir avec l'heure actuelle. Si non renseigné, le lien n'est jamais affiché publiquement | ❌ |

### 2.3 Wireframe

```
┌─────────────────────────────────────────────────┐
│  🔗 Lien public : /events/abc-123-def  [copier] │
│                                                 │
│  Nom :              [ Proba Blanc Chartreuse  ] │
│  Date :             [ 2026-09-15              ] │
│  Template :         [▼ Chartreuse 2026        ] │
│  Premier départ :   [ 07:30                   ] │
│  Lien Routechoices: [ https://...             ] │
│  Routechoices public : [ 14:00         ] [⏱]   │
│                                                 │
│  [ Initialiser depuis le template ]             │
│                                                 │
│                        [ Enregistrer ]          │
└─────────────────────────────────────────────────┘
```

> 💡 Le bouton **"Initialiser depuis le template"** n'apparaît que si un template est sélectionné.

---

## 3. Actions

| Action | Description |
|--------|-------------|
| **Enregistrer** | Sauvegarde en BDD sans quitter la page |
| **Initialiser depuis le template** | Copie les balises (avec `code` vide), les parcours et les temps PH depuis le template sélectionné vers l'événement. Écrase les données existantes. Demande confirmation via une popup |

---

## 4. Règles métier

- Le **template** détermine le registre de balises, les parcours et les temps PH de référence
- Les données du template sont importées dans l'événement via le bouton **"Initialiser depuis le template"** (pas de copie automatique)
- Le bouton déclenche une popup de confirmation : *"Les balises, parcours et barrières horaires seront réinitialisés depuis le template [Nom]. Les codes balises et les données existantes seront perdus. Continuer ?"*
- L'import copie `beacons` (avec `code: ""`), `courses` et `time_gates` depuis le template
- Après import, les données sont **indépendantes** du template (modifiables librement)
- L'heure du premier départ est utilisée par l'onglet [Horaires](schedule.md) pour calculer les horaires de chaque concurrent

