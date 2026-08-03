# Cahier des Charges Fonctionnel — O-Suivi

> **Version** : 1.5  
> **Date** : 2026-07-21  
> **Auteur** : Renaud d'Harreville  
> **Statut** : Brouillon

---

## 1. Contexte et objectifs

### 1.1 Contexte

Le **probatoire d'orientation** est une épreuve obligatoire pour entrer en formation d'Accompagnateur en Moyenne Montagne (AMM). 
Afin de préparer les candidats, des **probatoires blancs** (épreuves d'entraînement) sont organisés régulièrement par une équipe de professionnels.

Actuellement, la gestion de ces événements repose sur un **tableur Google Sheets** : ordres de départ, suivi des portes horaires, saisie manuelle des temps, résultats… 
Cette méthode atteint ses limites en termes de fiabilité, de lisibilité temps réel, et de facilité d'utilisation sur le terrain.

### 1.2 Objectifs du projet

Développer une application nommée **o Suivi** qui permet de :

1. **Créer et configurer** un événement probatoire blanc
2. **Gérer le départ** des concurrents de manière fluide
3. **Suivre en temps réel** l'avancement de chaque concurrent pendant l'épreuve
4. **Valider les passages** aux portes horaires et balises (automatique + manuel)
5. **Afficher les résultats** provisoires et finaux aux organisateurs et aux concurrents

### 1.3 Contraintes majeures

| Contrainte            | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **Hors-ligne**        | L'app doit fonctionner en zone de faible/absence de connectivité (montagne) |
| **Multi-utilisateur** | Plusieurs organisateurs simultanés (droits égaux)                           |
| **Robustesse**        | Toujours pouvoir pallier une défaillance technique par une saisie manuelle  |
| **Simplicité**        | Utilisable sur le terrain, sous stress, par des non-techniciens             |

---

## 2. Utilisateurs et rôles

### 2.1 Organisateurs (Encadrants)

- Équipe de plusieurs personnes avec les **mêmes droits d'accès**
- Responsables de la création d'événement, du suivi en direct, et de la validation des résultats
- Accèdent à l'intégralité de l'application (vues admin)

### 2.2 Stagiaires (Concurrents / Candidats)

- 10 à 50 personnes par événement
- Accèdent **uniquement** à leur espace via un **lien public commun** de l'événement
- **Identification** : le lien affiche la liste des participants ; le stagiaire sélectionne son nom pour accéder à son espace personnel. Son nom/prénom reste affiché en haut de l'écran pour vérification. En cas d'erreur, il peut revenir au lien commun et re-sélectionner
- Pendant l'épreuve : saisie de codes balises (aucun retour de validation)
- Après leur épreuve : accèdent aux **résultats provisoires de l'ensemble des stagiaires**
- **Accès public** : un lien partageable (`/events/{uuid}`) permet de consulter les résultats et d'éditer les balises de tout concurrent, sans authentification (voir [§5.4](views/public_results.md))

---

## 3. Concepts métier (Glossaire)

| Terme                         | Définition                                                                                                                                                                                                                                                                                                                                                                           |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Probatoire blanc**          | Épreuve d'entraînement simulant le probatoire officiel d'orientation AMM                                                                                                                                                                                                                                                                                                             |
| **PH (Porte Horaire)**        | Point de passage obligatoire avec une contrainte de temps. Une balise est marquée PH (booléen) ; le numéro de PH est calculé dynamiquement selon l'ordre de la balise dans le parcours (1ère balise PH = PH1, 2ème = PH2, etc.). Le nombre de PH est **variable** par parcours. Les PH sont aussi des balises à valider. Chaque PH a une borne max obligatoire et une borne min **optionnelle** (à la discrétion de l'organisateur). Le temps de chaque PH est **par section** (non cumulatif depuis le départ). La validation est déclenchée **par le stagiaire** (saisie du code balise PH) : cela arrête le chrono de la section en cours et démarre simultanément celui de la section suivante. L'encadrant peut modifier la validation en cas de problème |
| **Section**                   | Portion du parcours entre deux PH (ou entre le départ et la PH1). Section N = segment avant PH(N). Le nombre de sections = nombre de PH du parcours                                                                                                                                   |
| **Balise**                    | Point de passage physique identifié par un numéro et un tag. Un même numéro peut avoir plusieurs variantes (ex : 5-NO, 5-SE). Le concurrent doit valider toutes les balises **de son parcours**, dans le **bon ordre**. Le code 2 lettres est attribué par événement et est **unique par balise** (deux balises ne partagent jamais le même code au sein d'un événement)               |
| **Tous postes**               | Registre référençant l'ensemble des balises positionnées en forêt, toutes variantes confondues. Sert de base à la création des parcours                                                                                                                                                                                                                                              |
| **Parcours**                  | Itinéraire défini composé d'une sélection ordonnée de balises (une variante par numéro). Un événement comporte typiquement 4 à 6 parcours différents, numérotés de 1 à 6. Les balises "uniques" (dont les PH) sont communes à tous les parcours                                                                                                                                      |
| **km-ef (kilomètre-effort)**  | Unité de mesure de la difficulté d'un parcours. Formule : distance topographique (km) + 10 × D+ cumulé (km) + 1 × D- cumulé (km). Sert de base au calcul théorique des temps                                                                                                                                                                                                         |
| **Temps homme / Temps femme** | Les parcours sont identiques physiquement, mais les femmes disposent d'un temps supplémentaire à chaque PH                                                                                                                                                                                                                                                                           |
| **Routechoices**              | Plateforme externe de tracking GPS en direct. En v1, seul un lien URL vers l'événement Routechoices est intégré (pas d'intégration technique)                                                                                                                                                                                                                                        |
| **Tracker**                   | Balise GPS prêtée au concurrent par l'organisation, utilisée par la plateforme Routechoices                                                                                                                                                                                                                                                                                          |

---

## 4. Périmètre fonctionnel

### 4.1 Vue d'ensemble des modules

```
┌─────────────────────────────────────────────────────────┐
│                      O-SUIVI APP                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │  CONFIGURATION  │  │     ÉPREUVE EN COURS         │  │
│  │                 │  │                              │  │
│  │  • Événement    │  │  • Vue Départ                │  │
│  │  • Parcours     │  │  • Vue Suivi (synthétique)   │  │
│  │  • Participants │  │  • Vue Résultats provisoires │  │
│  └─────────────────┘  └──────────────────────────────┘  │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │         ACCÈS PUBLIC (lien partagé)                │ │
│  │                                                    │ │
│  │  • Résultats provisoires   • Édition balises       │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Description détaillée des fonctionnalités

### 5.1 Module Configuration

→ **Spécifications détaillées** :
- [Page d'accueil admin](views/admin_home.md)
- [Templates de probatoire](views/templates/_overview.md) (registre balises, parcours, temps PH)
- [Événements](views/events/_overview.md) (infos générales, participants, horaires, codes balises, barrières horaires)

Configuration des templates de probatoire (modèles réutilisables) et des événements (probatoires blancs). 
Les templates définissent les balises, parcours et temps PH de référence. Les événements ajoutent les participants, les horaires, les codes 2 lettres et les éventuels ajustements de temps.

---

### 5.2 Module Départ (Vue Encadrants)

→ **Spécification détaillée** : [views/depart.md](views/depart.md)

Visualiser et gérer le départ séquentiel des concurrents. L'encadrant confirme manuellement chaque départ via un bouton dédié. L'horaire de départ est toujours modifiable.

---

### 5.3 Module Suivi — Vue Synthétique (Vue Encadrants)

→ **Spécification détaillée** : [views/suivi.md](views/suivi.md)

Surveillance en temps réel de l'avancement des concurrents. Liste avec code couleur par statut, détail dépliable par concurrent (portes horaires, balises, actions encadrant), historique des modifications.

---

### 5.4 Module Résultats Provisoires (Vue partagée Encadrants + Stagiaires)

→ **Spécification détaillée** : [views/resultats.md](views/resultats.md)

Récapitulatif de la performance de chaque concurrent : statut par PH, résultat global (validé/non validé), vue détaillée dépliable avec temps par section, liste des balises, et lien Routechoices.

Un **accès public** alternatif (sans authentification) est disponible via un lien partageable. Il affiche les mêmes résultats et permet en plus l'édition des balises de chaque concurrent.
→ Spécifications : [views/public_results.md](views/public_results.md) et [views/public_beacon_edit.md](views/public_beacon_edit.md)

---

### 5.5 Accès Public

→ **Spécifications détaillées** : [views/public_events_list.md](views/public_events_list.md), [views/public_results.md](views/public_results.md) et [views/public_beacon_edit.md](views/public_beacon_edit.md)

- Une **page de liste des événements** (`/events`) permet de consulter tous les événements disponibles, triés par date décroissante, et d'accéder aux résultats de chacun. Un lien vers cette page est présent sur la page de login.
- Un lien partageable (`/events/{uuid}`) permet à quiconque de consulter les résultats provisoires de tous les concurrents et d'éditer les balises de chaque concurrent, sans authentification. Les modifications sont tracées avec `author_id = "public"`.

---

## 6. Règles métier importantes

### 6.1 Portes Horaires

- Le nombre de PH est **variable** par parcours (déterminé par le nombre de balises marquées PH dans le registre).
- Chaque PH a une **borne supérieure** (temps max) obligatoire et une **borne inférieure** (temps min) **optionnelle** — à la discrétion de l'organisateur. Si pas de borne min, un stagiaire rapide est toujours validé.
- Les bornes sont **différenciées par sexe** (les femmes ont plus de temps).
- Le temps est compté **par section** : depuis la PH précédente (ou depuis le départ pour la PH1). Ce n'est **pas un cumul** depuis le départ.
- La validation de la PH est **déclenchée par le stagiaire** (saisie du code + confirmation de validation/départ). L'encadrant peut modifier la validation en cas de problème.
- **Mécanisme arrivée/validation** : le stagiaire peut signaler son arrivée à la PH sans valider immédiatement (pause), puis valider quand il est prêt à repartir. Le temps officiel de la section est calculé jusqu'à la **validation** (pas l'arrivée).
- Le candidat est **seul responsable** de son chronométrage : l'application ne lui fournit aucune indication de temps pendant l'épreuve.
- Un candidat trop rapide (sous le temps min) ou trop lent (au-dessus du temps max) est considéré hors temps.
- Les temps de référence sont calculés par l'organisation en amont (formule km-ef) et peuvent être **ajustés par épreuve** selon les conditions réelles.

#### Formules de référence (indicatives) :

> ⚠️ Ces formules servent de base de calcul à l'organisation pour les probatoires blancs standards. Les temps réels saisis dans l'app peuvent différer et ne sont pas contraints par ces formules.

### 6.2 Balises

- Les codes 2 lettres sont **uniques par balise** au sein d'un événement (pas de doublon possible).
- Les codes peuvent être attribués **tardivement**, y compris **après le début de l'épreuve** (balises posées le matin même) : la validation des saisies contre les codes attendus n'est possible qu'une fois tous les codes renseignés.
- Chaque parcours a sa propre liste ordonnée de balises (15 à 20 au total sur un parcours officiel).
- Le concurrent doit valider **toutes** les balises de son parcours.
- Les balises doivent être validées **dans l'ordre**.
- Valider une balise qui n'est pas sur son parcours = élimination (si le code saisi correspond à une balise d'un autre parcours, cela signifie que le stagiaire s'est trompé de chemin).
- Le code saisi est **immuable** une fois confirmé par le stagiaire. En cas d'erreur avérée, seul un encadrant peut modifier un code après l'arrivée du stagiaire.
- Les PH sont un sous-ensemble des balises (certaines balises sont aussi des PH).

### 6.3 Modifications par les encadrants

- Un encadrant peut **modifier** les données d'un concurrent à tout moment : codes balises, horaires de passage, statut PH, etc.
- Toute modification par un encadrant est **automatiquement enregistrée** dans l'historique des modifications (avec horodatage et identité de l'encadrant)
- Un **commentaire** est obligatoire pour les abandons et les DNS
- L'historique complet est consultable dans la vue Suivi (détail d'un concurrent)
- Il n'y a pas de concept de "forçage" distinct : chaque intervention est une simple écriture, traçable via l'historique

### 6.4 Résolution des conflits multi-encadrants

- En cas de modifications simultanées (offline), la règle est **"timestamp wins"** : le serveur traite les actions dans l'ordre chronologique de leur horodatage local.
- **L'historique complet** de toutes les actions est conservé et affiché, permettant aux encadrants de voir ce qui s'est passé et de corriger si nécessaire.
- Ce mécanisme offre à la fois simplicité de mise en œuvre et traçabilité complète.

### 6.5 Spécificités du probatoire blanc (vs. examen officiel)

Le probatoire blanc est un **entraînement** : certaines règles sont assouplies par rapport à l'examen officiel.

| Aspect                      | Examen officiel                   | Proba blanc                                        |
|-----------------------------|-----------------------------------|----------------------------------------------------|
| Validation des balises      | Puce électronique                 | Code 2 lettres via l'app                           |
| Élimination en section 1    | Immédiate (ne peut pas continuer) | Le candidat **peut continuer** (mode entraînement) |
| Élimination autres sections | Effective                         | Le candidat **peut continuer**                     |
| Matériel obligatoire        | Contrôlé, éliminatoire            | Non imposé (poids du sac noté à titre indicatif)   |
| Arrêt si trop rapide        | Le candidat gère seul             | Pas d'intervention de l'app, le candidat gère seul |
| Résultats                   | Officiels après délibération jury | Provisoires, à visée pédagogique                   |

---

## 7. Données et intégrations

### 7.1 Données d'entrée

| Donnée               | Format                       | Source         |
|----------------------|------------------------------|----------------|
| Liste participants   | Fichier (CSV/Excel)          | Organisateur   |
| Infos participant    | Nom, Prénom, Téléphone, Sexe | Fichier import |
| Modèle de probatoire | Saisie dans l'app            | Organisateur   |

### 7.2 Données produites

- Heures de départ réelles
- Temps de passage aux PH (heure d'arrivée + heure de validation/départ → temps de pause calculable)
- Codes balises saisis (avec horodatage)
- Poids des sacs (départ/arrivée)
- Historique des modifications encadrants (avec horodatage, identité et commentaires)
- Statut tracker (prêté/rendu) par concurrent
- Résultats finaux (validé/non validé)


---

## 8. Contraintes non-fonctionnelles

| Contrainte        | Exigence                                                                                        |
|-------------------|-------------------------------------------------------------------------------------------------|
| **Hors-ligne**    | L'application doit fonctionner sans connexion internet pour **les encadrants ET les stagiaires**. Synchronisation bidirectionnelle quand le réseau revient |
| **Responsive**    | Utilisable sur smartphone (terrain) et desktop (PC au camp de base)                             |
| **Performance**   | Mise à jour fluide du suivi temps réel pour 50 concurrents                                      |
| **Fiabilité**     | Aucune perte de données, même en cas de coupure réseau                                          |
| **Simplicité**    | Interface épurée, très simple pour les stagiaires                                               |
| **Accessibilité** | Couleurs + icônes/texte (ne pas reposer uniquement sur la couleur)                              |

---

## 9. Questions ouvertes / Points à approfondir


### Questions encore ouvertes

- Voir backlogs

---

## 10. Prochaines étapes

| #  | Document                                         | Objectif                                      |
|----|--------------------------------------------------|-----------------------------------------------|
| 01 | **Cahier des charges fonctionnel** (ce document) | Formaliser les besoins métier                 |
| 02 | **Maquettes / Wireframes**                       | Visualiser les écrans et les flux utilisateur |
| 03 | **Spécifications techniques**                    | Choix de stack, architecture, gestion offline |
| 04 | **Modèle de données**                            | Structure de la base de données               |
| 05 | **Plan de développement**                        | Découpage en sprints/itérations, priorisation |
| 06 | **Protocole de test terrain**                    | Scénarios de test en conditions réelles       |

---

## Annexes

### A. Flux utilisateur simplifié — Jour J

```
[Avant l'événement]
    Organisateur crée l'événement
    Import des participants
    Configuration des départs
    ↓
[Jour J — Départ]
    Pesée des sacs
    Départs séquentiels (horloge)
    ↓
[Épreuve en cours]
    Stagiaires : saisissent codes balises
    Encadrants : surveillent vue suivi
    Gestion des imprévus (modification par encadrant)
    ↓
[Dernière PH]
    Validation dernière PH
    Stagiaire saisit poids du sac (arrivée)
    Restitution tracker (page bloquante jusqu'à validation encadrant)
    ↓
[Après l'épreuve]
    Résultats provisoires affichés (visibles par encadrants ET stagiaires arrivés)
    Vérification par les encadrants
```

### B. Exemple de carte "tous postes" et parcours

```
Registre "tous postes" :
  Balise 1  — tag: unique     — PH: non
  Balise 2  — tag: NO         — PH: non
  Balise 2  — tag: SE         — PH: non
  Balise 3  — tag: unique     — PH: oui        ← Tous les parcours passent ici (= PH1)
  Balise 4  — tag: N          — PH: non
  Balise 4  — tag: S          — PH: non
  Balise 5  — tag: unique     — PH: non        ← Tous les parcours passent ici
  Balise 6  — tag: unique     — PH: oui        ← Tous les parcours passent ici (= PH2)
  ...

Parcours 1 (sélection) :
  Départ → [1-unique] → [2-NO] → [3-unique (=PH1)] → [4-N] → [5-unique] → [6-unique (=PH2)] → ...

Parcours 2 (sélection) :
  Départ → [1-unique] → [2-SE] → [3-unique (=PH1)] → [4-S] → [5-unique] → [6-unique (=PH2)] → ...

Note : Les codes 2 lettres (AB, CD, EF...) sont attribués lors de la création de l'événement.
Note : Le numéro de PH (PH1, PH2, ...) est calculé dynamiquement selon l'ordre de la balise PH dans le parcours.

Temps PH1 : min 45min / max 1h15 (H) — min 45min / max 1h25 (F)
Temps PH2 : min 30min / max 1h00 (H) — min 30min / max 1h10 (F)
Temps PH3 : max 45min (H) — max 55min (F)  [pas de borne min, choix de l'organisateur]
```
