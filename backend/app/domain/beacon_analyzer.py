from app.domain.competitor_state import CheckpointEntry, CompetitorState
from app.domain.time_utils import seconds_between
from app.schemas.events import EventBeacon
from app.schemas.results import BeaconResult


class BeaconAnalyzer:
    """Analyzes beacon passages: code validity, split times, cumulated section times."""

    def __init__(self, course_beacons: list[EventBeacon], state: CompetitorState) -> None:
        self._beacons = course_beacons
        self._state = state

    def analyze(self) -> list[BeaconResult]:
        results: list[BeaconResult] = []
        previous_ts = self._state.departure_time
        section_start_ts = self._state.departure_time

        for idx, beacon in enumerate(self._beacons):
            seq = idx + 1
            checkpoint = self._state.checkpoints.get(seq)

            result = self._build_result(beacon, seq, checkpoint, previous_ts, section_start_ts)
            results.append(result)

            if checkpoint:
                previous_ts = checkpoint.passage_time
                if beacon.is_ph:
                    section_start_ts = checkpoint.passage_time

        return results

    def _build_result(
        self,
        beacon: EventBeacon,
        sequence: int,
        checkpoint: CheckpointEntry | None,
        previous_ts: str | None,
        section_start_ts: str | None,
    ) -> BeaconResult:
        expected = beacon.code or None
        entered, passage_time, valid = self._validity(checkpoint, sequence, expected)

        return BeaconResult(
            sequence=sequence,
            beacon_number=beacon.number,
            tag=beacon.tag,
            is_ph=beacon.is_ph,
            expected_code=expected,
            entered_code=entered,
            valid=valid,
            split_time=seconds_between(previous_ts, passage_time),
            cumulated_section_time=seconds_between(section_start_ts, passage_time),
        )

    def _validity(
        self,
        checkpoint: CheckpointEntry | None,
        sequence: int,
        expected_code: str | None,
    ) -> tuple[str | None, str | None, bool | None]:
        """Return (entered_code, passage_time, valid)."""
        if checkpoint:
            if expected_code and checkpoint.code:
                valid = checkpoint.code.upper() == expected_code.upper()
            elif expected_code:
                valid = False  # Code expected but not provided
            else:
                valid = True
            return checkpoint.code, checkpoint.passage_time, valid

        if sequence in self._state.skipped:
            return None, None, False

        return None, None, None

