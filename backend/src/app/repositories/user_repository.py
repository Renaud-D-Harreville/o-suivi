import json

from pydantic import TypeAdapter

from app.config import DATA_DIR
from app.schemas.users import User

_USER_LIST_ADAPTER = TypeAdapter(list[User])


class UserRepository:
    """Loads, caches, and persists typed User objects from users.json."""

    _users_file = DATA_DIR / "users.json"

    def __init__(self) -> None:
        self._cache: list[User] | None = None

    def find_by_id(self, user_id: str) -> User | None:
        return next((u for u in self._all() if u.id == user_id), None)

    def find_by_credentials(self, username: str, password: str) -> User | None:
        """Find an organizer by username + password. Returns None if not found."""
        return next(
            (
                u
                for u in self._all()
                if u.username == username
                and u.password == password
                and u.role == "organizer"
            ),
            None,
        )

    def add(self, user: User) -> None:
        """Add a new user and persist."""
        users = self._all()
        users.append(user)
        self._persist(users)

    def update(self, user: User) -> None:
        """Update an existing user in place and persist."""
        users = self._all()
        for i, u in enumerate(users):
            if u.id == user.id:
                users[i] = user
                break
        self._persist(users)

    def save_all(self, users: list[User]) -> None:
        """Replace all users and persist. Use for bulk operations."""
        self._cache = users
        self._persist(users)

    def all(self) -> list[User]:
        """Return all users (cached, loaded on first access)."""
        return list(self._all())

    def _all(self) -> list[User]:
        if self._cache is None:
            if not self._users_file.exists():
                self._cache = []
            else:
                with self._users_file.open() as f:
                    self._cache = _USER_LIST_ADAPTER.validate_python(json.load(f))
        return self._cache  # type: ignore[return-value]

    def _persist(self, users: list[User]) -> None:
        """Write users to disk and update cache."""
        self._cache = users
        with self._users_file.open("w") as f:
            json.dump(
                [u.model_dump(exclude_none=False) for u in users],
                f,
                indent=2,
                ensure_ascii=False,
            )

