# Coding Skills — Implémentation Backend Python

> Guide concret pour l'implémentation. Exemples de code à suivre / à éviter.  
> **Dernière mise à jour** : 2026-07-28

---

## 1. Architecture en couches

```
routers/       → Thin controllers (HTTP → Service → Response). Max ~20 lignes par endpoint.
services/      → Orchestration. Coordonne repositories + domain. Aucune logique métier.
domain/        → Logique métier pure. Classes sans dépendance framework (sauf Pydantic).
repositories/  → Accès aux données. Retournent TOUJOURS des objets Pydantic typés.
schemas/       → Modèles Pydantic (DTOs, entités, unions).
```

**Règle** : les imports ne remontent jamais. `domain/` n'importe pas depuis `routers/` ni `services/`.

---

## 2. Toujours des objets typés — JAMAIS de `dict`

### ❌ INTERDIT

```python
def load_users() -> list[dict]:
    ...

def find_user(users: list[dict], user_id: str) -> dict | None:
    ...
```

### ✅ CORRECT

```python
from app.schemas.users import User

class UserRepository:
    def find_by_id(self, user_id: str) -> User | None:
        ...
```

**Règle** : Si une structure de données revient plus d'une fois, elle DOIT être un `BaseModel` Pydantic.

---

## 3. Pydantic pour le parsing — pas de match/case sur des dicts

### ❌ INTERDIT

```python
for log in raw_logs:
    match log.get("type"):
        case "departure":
            departed = True
        case "checkpoint":
            seq = log.get("data", {}).get("sequence")
            ...
```

### ✅ CORRECT

Utiliser le discriminated union Pydantic + `TypeAdapter` pour parser, puis travailler avec des objets typés :

```python
from pydantic import TypeAdapter
from app.schemas.logs import LogEntry

_ADAPTER = TypeAdapter(list[LogEntry])

entries = _ADAPTER.validate_python(raw_logs)
# entries est maintenant list[DepartureLog | CheckpointLog | ...]
```

---

## 4. Polymorphisme — pas de if/elif interminable

### ❌ INTERDIT

```python
def _apply(self, entry: LogEntry) -> None:
    if isinstance(entry, DepartureLog):
        self.departed = True
    elif isinstance(entry, DepartureCancelLog):
        self.departed = False
    elif isinstance(entry, CheckpointLog):
        ...
    elif isinstance(entry, CheckpointEditLog):
        ...
    # ... 15 branches
```

### ✅ CORRECT

Chaque sous-classe implémente son propre comportement :

```python
# Dans schemas/logs.py

class LogMetadata(BaseModel):
    creation_date: str   # quand l'action s'est produite (horloge client)
    received_at: str     # quand le serveur a reçu l'entrée
    author_id: str       # qui a effectué l'action

class BaseLogEntry(BaseModel):
    metadata: LogMetadata

    def apply_to(self, state: "CompetitorState") -> None:
        """No-op par défaut. Les sous-classes qui modifient l'état surchargent."""

class DepartureLog(BaseLogEntry):
    log_type: Literal["departure"] = "departure"
    data: DepartureData

    def apply_to(self, state: "CompetitorState") -> None:
        state.departed = True
        state.departure_time = to_hms(self.data.departure_time)

class CheckpointLog(BaseLogEntry):
    log_type: Literal["checkpoint"] = "checkpoint"
    data: CheckpointData

    def apply_to(self, state: "CompetitorState") -> None:
        state.checkpoints[self.data.sequence] = CheckpointEntry(
            sequence=self.data.sequence,
            code=self.data.code,
            passage_time=to_hms(self.data.passage_time),
        )
```

L'appelant fait simplement :

```python
for entry in entries:
    entry.apply_to(state)
```

**Principe** : Open/Closed. Ajouter un nouveau type de log = ajouter une classe, JAMAIS modifier du code existant.

---

## 5. Classes — pas de fonctions libres pour la logique métier

### ❌ INTERDIT

```python
def _compute_results_for_competitor(event_data, user, reg, logs):
    # 200 lignes de logique...
```

### ✅ CORRECT

```python
class BeaconAnalyzer:
    """Une seule responsabilité : analyser les passages balises."""

    def __init__(self, course_beacons: list[EventBeacon], state: CompetitorState) -> None:
        ...

    def analyze(self) -> list[BeaconResult]:
        ...
```

**Règle** : une classe = une responsabilité. Si la classe dépasse ~80 lignes, c'est qu'elle en fait trop.

---

## 6. Repositories — encapsuler l'accès aux données

### ❌ INTERDIT

```python
# Dans un router
USERS_FILE = DATA_DIR / "users.json"

def _load_users() -> list[dict]:
    with USERS_FILE.open() as f:
        return json.load(f)
```

### ✅ CORRECT

```python
class UserRepository:
    """Encapsule le chargement + cache + parsing des users."""

    def __init__(self) -> None:
        self._cache: list[User] | None = None

    def find_by_id(self, user_id: str) -> User | None:
        return next((u for u in self._all() if u.id == user_id), None)

    def _all(self) -> list[User]:
        if self._cache is None:
            raw = json.load(self._file.open())
            self._cache = TypeAdapter(list[User]).validate_python(raw)
        return self._cache
```

**Règle** : le JSON brut ne sort JAMAIS du repository. L'appelant ne voit que des objets typés.

---

## 7. Thin controllers (routers)

### ❌ INTERDIT

```python
@router.get("/resultats")
async def get_results(event_id: str) -> ResultsResponse:
    # 50 lignes de logique, chargement fichiers, calculs...
```

### ✅ CORRECT

```python
@router.get("/resultats", response_model=ResultsResponse)
async def get_results(event_id: str) -> ResultsResponse:
    service = ResultsService()
    return service.compute(event_id)
```

---

## 8. Modèles internes — tout est Pydantic

### ❌ INTERDIT

```python
checkpoints: dict[int, dict] = {}  # sequence -> {code, passage_time}
```

### ✅ CORRECT

```python
class CheckpointEntry(BaseModel):
    code: str | None = None
    passage_time: str | None = None

class CompetitorState(BaseModel):
    checkpoints: dict[int, CheckpointEntry] = Field(default_factory=dict)
```

---

## 9. Imports circulaires — résolution avec TYPE_CHECKING

Quand une classe du schéma doit connaître une classe du domain (ex: `apply_to(state: CompetitorState)`) :

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.competitor_state import CompetitorState
```

Cela résout l'import circulaire : à runtime il n'y a pas d'import, uniquement pour le type checking.

---

## 10. Nommage explicite — pas de noms génériques

### ❌ INTERDIT

```python
timestamp: str        # Timestamp de quoi ? Action ? Réception ? Passage ?
data: dict            # Data de quel type ?
value: float          # Valeur de quoi ?
items: list           # Items de quel type ?
```

### ✅ CORRECT

```python
creation_date: str    # Quand l'action a été créée (horloge client)
received_at: str      # Quand le serveur a reçu l'entrée
passage_time: str | None  # Quand le concurrent est passé à la balise (None si inconnu)
weight_kg: float      # Le poids du sac en kg
```

**Règle** : chaque nom de champ doit être compréhensible **sans lire le contexte** de la classe. Si tu dois ajouter un commentaire pour expliquer ce que le champ contient, c'est que le nom est trop vague.

---

## 11. Checklist avant de coder

- [ ] Le fichier fait-il plus de 150 lignes ? → Séparer
- [ ] Y a-t-il un `dict` en retour/paramètre ? → Remplacer par un `BaseModel`
- [ ] Y a-t-il un if/elif/match avec plus de 3 branches sur un type ? → Polymorphisme
- [ ] Y a-t-il de la logique métier dans un router ? → Extraire en service/domain
- [ ] Y a-t-il du code dupliqué entre routers ? → Extraire en repository/service
- [ ] Un modèle existant couvre-t-il déjà ce besoin ? → Réutiliser

