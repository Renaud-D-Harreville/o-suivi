import uuid

from fastapi import HTTPException

from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import EventRegistration
from app.schemas.registrations import RegistrationCreate, RegistrationDetail, RegistrationUpdate
from app.schemas.users import User


class RegistrationService:
    """Orchestrates registration logic: user creation, deduplication, CRUD."""

    def __init__(
        self,
        events: EventRepository | None = None,
        users: UserRepository | None = None,
    ) -> None:
        self._events = events or EventRepository()
        self._users = users or UserRepository()

    def list_all(self, event_id: str) -> list[RegistrationDetail]:
        registrations = self._events.get_registrations(event_id)
        result: list[RegistrationDetail] = []
        for reg in registrations:
            user = self._users.find_by_id(reg.user_id)
            if not user:
                continue
            result.append(self._to_detail(user, reg))
        return result

    def add(self, event_id: str, body: RegistrationCreate) -> RegistrationDetail:
        registrations = self._events.get_registrations(event_id)
        registered_ids = {r.user_id for r in registrations}

        # Check for duplicate
        for user in self._find_all_users():
            if (
                user.first_name.lower() == body.first_name.lower()
                and user.last_name.lower() == body.last_name.lower()
                and user.id in registered_ids
            ):
                raise HTTPException(status_code=409, detail="Participant already registered")

        # Create user
        user = self._create_user(body)
        self._users.add(user)

        # Add registration
        reg = EventRegistration(user_id=user.id)
        registrations.append(reg)
        self._events.set_registrations(event_id, registrations)

        return self._to_detail(user, reg)

    def remove(self, event_id: str, user_id: str) -> None:
        registrations = self._events.get_registrations(event_id)
        new_registrations = [r for r in registrations if r.user_id != user_id]
        if len(new_registrations) == len(registrations):
            raise HTTPException(status_code=404, detail="Registration not found")
        self._events.set_registrations(event_id, new_registrations)

    def replace_all(self, event_id: str, entries: list[RegistrationCreate]) -> list[RegistrationDetail]:
        old_registrations = self._events.get_registrations(event_id)
        all_users = self._find_all_users()

        new_registrations: list[EventRegistration] = []
        result: list[RegistrationDetail] = []

        for entry in entries:
            matched_user = self._match_user(entry, old_registrations, all_users)

            if matched_user:
                # Update existing user data
                updated = matched_user.model_copy(update={
                    "first_name": entry.first_name,
                    "last_name": entry.last_name,
                    "sex": entry.sex,
                    "phone": entry.phone,
                    "routechoices_id": entry.routechoices_id or None,
                })
                # Replace in all_users list
                for i, u in enumerate(all_users):
                    if u.id == matched_user.id:
                        all_users[i] = updated
                        break
                # Preserve existing registration fields
                old_reg = next((r for r in old_registrations if r.user_id == matched_user.id), None)
                reg = old_reg if old_reg else EventRegistration(user_id=matched_user.id)
                # Update routechoices_short_name from entry
                reg = reg.model_copy(update={"routechoices_short_name": entry.routechoices_short_name or None})
                new_registrations.append(reg)
                result.append(self._to_detail(updated, reg))
            else:
                # Create new user
                user = self._create_user(entry)
                all_users.append(user)
                reg = EventRegistration(
                    user_id=user.id,
                    routechoices_short_name=entry.routechoices_short_name or None,
                )
                new_registrations.append(reg)
                result.append(self._to_detail(user, reg))

        self._users.save_all(all_users)
        self._events.set_registrations(event_id, new_registrations)
        return result

    def update(self, event_id: str, user_id: str, body: RegistrationUpdate) -> RegistrationDetail:
        registrations = self._events.get_registrations(event_id)
        reg = next((r for r in registrations if r.user_id == user_id), None)
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        # Apply updates
        updates = body.model_dump(exclude_unset=True)
        updated_reg = reg.model_copy(update=updates)
        registrations = [updated_reg if r.user_id == user_id else r for r in registrations]
        self._events.set_registrations(event_id, registrations)

        user = self._users.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_detail(user, updated_reg)

    def _match_user(
        self,
        entry: RegistrationCreate,
        old_registrations: list[EventRegistration],
        all_users: list[User],
    ) -> User | None:
        """Match by routechoices_id first, then by name."""
        old_user_ids = {r.user_id for r in old_registrations}

        if entry.routechoices_id:
            for u in all_users:
                if u.id in old_user_ids and u.routechoices_id == entry.routechoices_id:
                    return u

        for u in all_users:
            if (
                u.id in old_user_ids
                and u.first_name.lower() == entry.first_name.lower()
                and u.last_name.lower() == entry.last_name.lower()
            ):
                return u

        return None

    def _find_all_users(self) -> list[User]:
        """Return a mutable copy of all users."""
        return self._users.all()

    @staticmethod
    def _create_user(body: RegistrationCreate) -> User:
        return User(
            id=str(uuid.uuid4()),
            routechoices_id=body.routechoices_id or None,
            role="competitor",
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
            sex=body.sex,
        )

    @staticmethod
    def _to_detail(user: User, reg: EventRegistration) -> RegistrationDetail:
        return RegistrationDetail(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            sex=user.sex or "H",
            phone=user.phone,
            routechoices_id=user.routechoices_id,
            routechoices_short_name=reg.routechoices_short_name,
            course_number=reg.course_number,
            start_order=reg.start_order,
            start_time_planned=reg.start_time_planned,
            tracker_number=reg.tracker_number,
        )

