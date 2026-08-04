from app.domain.competitor_state import CompetitorState
from app.domain.time_utils import seconds_between
from app.schemas.events import EventBeacon, EventDetail
from app.schemas.splits import BeaconPairSplits, SplitEntry


class SplitCalculator:
    """Extracts beacon pairs from courses and computes split times."""

    def extract_pairs(self, event: EventDetail) -> list[tuple[int | None, int]]:
        """Extract all unique consecutive beacon pairs across all courses.

        Returns a sorted list of (from_beacon_id | None, to_beacon_id) tuples.
        None as from_beacon_id means "from departure".
        """
        pairs: set[tuple[int | None, int]] = set()

        for course in event.courses:
            beacon_ids = [b.id for b in course.beacons]
            if not beacon_ids:
                continue
            # First pair: Départ → first beacon
            pairs.add((None, beacon_ids[0]))
            # Subsequent pairs
            for i in range(len(beacon_ids) - 1):
                pairs.add((beacon_ids[i], beacon_ids[i + 1]))

        return sorted(pairs, key=self._pair_sort_key(event))

    def compute_splits(
        self,
        pairs: list[tuple[int | None, int]],
        states: dict[str, CompetitorState],
        registrations_course: dict[str, int | None],
        event: EventDetail,
    ) -> list[BeaconPairSplits]:
        """Compute split times for all pairs and all competitors."""
        # Build a map: user_id → set of beacon_ids in their course
        user_course_beacons: dict[str, list[int]] = {}
        for user_id, course_number in registrations_course.items():
            if course_number is None:
                continue
            for course in event.courses:
                if course.number == course_number:
                    user_course_beacons[user_id] = [b.id for b in course.beacons]
                    break

        results: list[BeaconPairSplits] = []
        for from_id, to_id in pairs:
            entries = self._compute_pair(from_id, to_id, states, user_course_beacons)
            entries.sort(key=lambda e: e.split_seconds)
            results.append(BeaconPairSplits(
                from_beacon_id=from_id,
                to_beacon_id=to_id,
                splits=entries,
            ))
        return results

    def _compute_pair(
        self,
        from_id: int | None,
        to_id: int,
        states: dict[str, CompetitorState],
        user_course_beacons: dict[str, list[int]],
    ) -> list[SplitEntry]:
        entries: list[SplitEntry] = []

        for user_id, state in states.items():
            course_beacons = user_course_beacons.get(user_id)
            if course_beacons is None:
                continue

            # Check this pair exists in the competitor's course
            if not self._pair_in_course(from_id, to_id, course_beacons):
                continue

            from_time = self._get_passage_time(from_id, state, course_beacons)
            to_time = self._get_passage_time(to_id, state, course_beacons)

            if from_time is None or to_time is None:
                continue

            split = seconds_between(from_time, to_time)
            if split is not None and split > 0:
                entries.append(SplitEntry(user_id=user_id, split_seconds=split))

        return entries

    def _pair_in_course(
        self, from_id: int | None, to_id: int, course_beacons: list[int]
    ) -> bool:
        if to_id not in course_beacons:
            return False
        if from_id is None:
            # Départ → first beacon
            return course_beacons[0] == to_id
        if from_id not in course_beacons:
            return False
        idx_from = course_beacons.index(from_id)
        idx_to = course_beacons.index(to_id)
        return idx_to == idx_from + 1

    def _get_passage_time(
        self, beacon_id: int | None, state: CompetitorState, course_beacons: list[int]
    ) -> str | None:
        if beacon_id is None:
            # "Départ" → use departure_time
            return state.departure_time

        # Find the sequence (1-based position in the course)
        if beacon_id not in course_beacons:
            return None
        sequence = course_beacons.index(beacon_id) + 1

        checkpoint = state.checkpoints.get(sequence)
        if checkpoint and checkpoint.passage_time:
            return checkpoint.passage_time
        return None

    def _pair_sort_key(self, event: EventDetail):
        """Return a sort key function for beacon pairs."""
        beacon_map: dict[int, EventBeacon] = {b.id: b for b in event.beacons}

        def key(pair: tuple[int | None, int]) -> tuple:
            from_id, to_id = pair
            if from_id is None:
                from_key = (0, "")
            else:
                b = beacon_map.get(from_id)
                from_key = (b.number, b.tag) if b else (0, "")

            b2 = beacon_map.get(to_id)
            to_key = (b2.number, b2.tag) if b2 else (0, "")

            return (from_key, to_key)

        return key

