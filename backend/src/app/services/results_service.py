from app.domain.beacon_analyzer import BeaconAnalyzer
from app.domain.competitor_state import CompetitorState
from app.domain.results_calculator import ResultsCalculator
from app.domain.section_validator import SectionValidator
from app.domain.time_utils import seconds_between
from app.repositories.event_repository import EventRepository
from app.repositories.log_repository import LogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import EventBeacon, EventDetail, EventRegistration
from app.schemas.results import CompetitorResult, ResultsResponse, SectionResult
from app.schemas.templates import Gate


class ResultsService:
    """Orchestrates result computation for all competitors of an event."""

    def __init__(
        self,
        events: EventRepository | None = None,
        users: UserRepository | None = None,
        logs: LogRepository | None = None,
    ) -> None:
        self._events = events or EventRepository()
        self._users = users or UserRepository()
        self._logs = logs or LogRepository()
        self._calc = ResultsCalculator()

    def compute(self, event_id: str) -> ResultsResponse:
        event = self._events.load(event_id)
        results = [
            self._compute_one(event, reg)
            for reg in event.registrations
            if self._users.find_by_id(reg.user_id)
        ]
        results.sort(key=self._calc.sort_key)

        return ResultsResponse(
            routechoices_url=event.routechoices_url,
            public_routechoices_time=event.public_routechoices_time,
            event_date=event.date,
            competitors=results,
        )

    def _compute_one(self, event: EventDetail, reg: EventRegistration) -> CompetitorResult:
        user = self._users.find_by_id(reg.user_id)
        assert user is not None  # Filtered upstream

        course_number = reg.course_number
        beacons = self._events.get_course_beacons(event, course_number)
        gates = self._events.get_time_gates(event, course_number)

        state = self._build_state(event.id, user.id)
        beacon_results = BeaconAnalyzer(beacons, state).analyze()
        section_results = self._validate_sections(gates, beacons, state, user.sex, beacon_results)

        arrival_time = self._calc.finish_time(state, gates, beacons)
        total_time = seconds_between(state.departure_time, arrival_time)
        running_times = [s.running_time for s in section_results if s.running_time is not None]

        return CompetitorResult(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            sex=user.sex,
            course_number=course_number,
            valid_global=self._calc.global_validity(state, section_results),
            dns=state.dns,
            abandoned=state.abandoned,
            finished=state.dns or state.abandoned or arrival_time is not None,
            has_tracker=bool(reg.tracker_number),
            tracker_returned=state.tracker_returned,
            bag_weight_start=state.bag_weight_start,
            bag_weight_end=state.bag_weight_end,
            departure_time=state.departure_time,
            arrival_time=arrival_time,
            total_time=total_time,
            total_running_time=sum(running_times) if running_times else None,
            sections=section_results,
            beacons=beacon_results,
        )

    def _build_state(self, event_id: str, user_id: str) -> CompetitorState:
        logs = self._logs.load(event_id, user_id)
        state = CompetitorState()
        for entry in logs:
            entry.apply_to(state)
        return state

    def _validate_sections(
        self,
        gates: list[Gate],
        beacons: list[EventBeacon],
        state: CompetitorState,
        sex: str | None,
        beacon_results: list,
    ) -> list[SectionResult]:
        ph_sequences = self._calc.ph_gate_sequences(beacons)
        results: list[SectionResult] = []
        previous_ph_time = state.departure_time

        for gate in gates:
            gate_seq = ph_sequences.get(gate.gate)
            if gate_seq is None:
                results.append(SectionResult(gate=gate.gate))
                continue

            prev_seq = self._calc.prev_gate_sequence(gates, gate, ph_sequences)
            validator = SectionValidator(gate, gate_seq, prev_seq, sex, state, beacon_results)
            result = validator.validate(previous_ph_time)
            results.append(result)

            checkpoint = state.checkpoints.get(gate_seq)
            if checkpoint:
                previous_ph_time = checkpoint.passage_time

        return results

