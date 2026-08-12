from app.domain.competitor_state import CompetitorState
from app.schemas.events import EventBeacon
from app.schemas.results import CompetitorResult, SectionResult
from app.schemas.templates import Gate


class ResultsCalculator:
    """Pure domain logic for computing results: validity, finish time, sorting."""

    @staticmethod
    def ph_gate_sequences(beacons: list[EventBeacon]) -> dict[str, int]:
        """Map gate label -> sequence (1-based index) for PH beacons.

        PH labels are computed dynamically: first PH beacon = "PH1", second = "PH2", etc.
        """
        result: dict[str, int] = {}
        ph_index = 0
        for idx, b in enumerate(beacons):
            if b.is_ph:
                ph_index += 1
                result[f"PH{ph_index}"] = idx + 1
        return result

    @staticmethod
    def prev_gate_sequence(gates: list[Gate], current: Gate, ph_map: dict[str, int]) -> int:
        """Find the sequence of the gate preceding `current`, or 0 if first."""
        prev_seq = 0
        for g in gates:
            if g.gate == current.gate:
                break
            seq = ph_map.get(g.gate)
            if seq:
                prev_seq = seq
        return prev_seq

    @staticmethod
    def finish_time(
        state: CompetitorState,
        gates: list[Gate],
        beacons: list[EventBeacon],
    ) -> str | None:
        """Return the timestamp of the last PH checkpoint, only if the competitor finished."""
        if not gates:
            return None
        ph_sequences = ResultsCalculator.ph_gate_sequences(beacons)
        last_gate = gates[-1]
        seq = ph_sequences.get(last_gate.gate)
        if seq:
            cp = state.checkpoints.get(seq)
            if cp:
                return cp.passage_time
        return None

    @staticmethod
    def global_validity(state: CompetitorState, sections: list[SectionResult]) -> bool | None:
        """Compute overall race validity from section results."""
        if state.dns or not state.departed:
            return None
        if not sections:
            return None
        if all(s.valid is not None for s in sections):
            return all(s.valid is True for s in sections)
        return None

    @staticmethod
    def sort_key(competitor: CompetitorResult) -> tuple:
        """Sort key: arrived first, then in-progress, then DNS last."""
        if competitor.dns:
            return (2, "")
        if competitor.arrival_time is None:
            return (1, "")
        return (0, competitor.arrival_time)

