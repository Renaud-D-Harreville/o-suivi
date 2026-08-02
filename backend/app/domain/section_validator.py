from app.domain.competitor_state import CompetitorState
from app.domain.time_utils import seconds_between
from app.schemas.results import BeaconResult, SectionResult
from app.schemas.templates import Gate


class SectionValidator:
    """Validates a single section (PH gate): time bounds, beacon codes, order."""

    def __init__(
        self,
        gate: Gate,
        gate_sequence: int,
        prev_gate_sequence: int,
        sex: str | None,
        state: CompetitorState,
        beacon_results: list[BeaconResult],
    ) -> None:
        self._gate = gate
        self._gate_seq = gate_sequence
        self._prev_gate_seq = prev_gate_sequence
        self._sex = sex
        self._state = state
        self._section_beacons = [
            b for b in beacon_results
            if prev_gate_sequence < b.sequence <= gate_sequence
        ]

    def validate(self, previous_ph_time: str | None) -> SectionResult:
        checkpoint = self._state.checkpoints.get(self._gate_seq)
        ph_arrival = self._state.ph_arrivals.get(self._gate_seq)
        validation_time = checkpoint.passage_time if checkpoint else None

        section_time = seconds_between(previous_ph_time, validation_time)
        running_time = seconds_between(previous_ph_time, ph_arrival)
        pause_time = seconds_between(ph_arrival, validation_time)
        delay = self._compute_delay(section_time)
        valid = self._compute_validity(validation_time, delay)

        return SectionResult(
            gate=self._gate.gate,
            valid=valid,
            delay=delay,
            section_time=section_time,
            running_time=running_time,
            pause_time=pause_time,
        )

    def _compute_delay(self, section_time: int | None) -> int | None:
        if section_time is None:
            return None

        section_minutes = section_time / 60.0
        min_bound, max_bound = self._time_bounds()

        if min_bound is not None and section_minutes < min_bound:
            return int(section_minutes - min_bound)
        if max_bound is not None and section_minutes > max_bound:
            return int(section_minutes - max_bound)
        return None

    def _time_bounds(self) -> tuple[int | None, int | None]:
        if self._sex == "F":
            return self._gate.min_f, self._gate.max_f
        return self._gate.min_m, self._gate.max_m

    def _compute_validity(self, validation_time: str | None, delay: int | None) -> bool | None:
        if not validation_time:
            return None

        time_ok = delay is None
        beacons_ok = all(b.valid is True for b in self._section_beacons)
        order_ok = self._check_order()

        return time_ok and beacons_ok and order_ok

    def _check_order(self) -> bool:
        """Verify beacons were validated in sequence order."""
        passage_times: list[str] = []
        for b in self._section_beacons:
            cp = self._state.checkpoints.get(b.sequence)
            if cp:
                if cp.passage_time:
                    passage_times.append(cp.passage_time)
            elif b.sequence not in self._state.skipped:
                return False  # Not reached and not skipped = invalid
        return passage_times == sorted(passage_times)

