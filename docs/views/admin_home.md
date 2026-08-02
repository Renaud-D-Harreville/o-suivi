# Page d'accueil Admin

> **Statut** : Validé  
> **Référence** : [Cahier des charges §5.1](../01_cahier_des_charges_fonctionnel.md)

---

## 1. Objectif

Point d'entrée principal pour les encadrants après authentification. Permet d'accéder aux templates de probatoire et aux événements.

---

## 2. Accès

Encadrants uniquement (authentifiés via JWT).

---

## 3. Structure de l'écran

### 3.1 Navigation par onglets

Deux onglets principaux en haut de la page :

```
┌──────────────────┬──────────────────┐
│    TEMPLATES     │   ÉVÉNEMENTS     │
└──────────────────┴──────────────────┘
```

### 3.2 Onglet Templates

- **Liste de tous les templates** de probatoire existants
- Chaque ligne affiche le nom du template
- Clic sur une ligne → ouvre le template (voir [templates/_overview.md](templates/_overview.md))
- **Bouton "Nouveau template"** → popup de création (demande le nom) → redirige vers la vue template

### 3.3 Onglet Événements

- **Liste de tous les événements** existants
- Chaque ligne affiche : nom de l'événement, date
- Clic sur une ligne → ouvre l'événement (voir [events/_overview.md](events/_overview.md))
- **Bouton "Nouvel événement"** → popup de création (demande le nom) → redirige vers la vue événement

---

## 4. Popup de création

Identique pour les templates et les événements :

```
┌─────────────────────────────────────┐
│  Nouveau template / événement       │
│                                     │
│  Nom : [________________________]   │
│                                     │
│        [ Annuler ]  [ Créer ]       │
└─────────────────────────────────────┘
```

- Champ **nom** obligatoire
- Bouton **Créer** → crée l'objet en BDD et redirige vers sa vue dédiée
- Bouton **Annuler** → ferme la popup

---

## 5. Visibilité

- Tous les templates sont visibles par tous les encadrants
- Tous les événements sont visibles par tous les encadrants
- Pas de notion de propriété individuelle

