import { type Ref } from "vue";
import type { TrackingCompetitor } from "../types/competitor";
import type { BeaconInput } from "../types/log";
import { hmsToIsoTimestamp, toLocalISO, formatTime, formatIsoToHms } from "../utils/date";
import { hasCodeChanged, hasTimeChanged, codeToPayload } from "../utils/beacon-validation";
import { computeCurrentPh } from "../utils/competitor-state";
import { apiFetch } from "../utils/api";

export function useBeaconSave(
  eventId: string,
  competitors: Ref<TrackingCompetitor[]>,
  beaconInputs: Ref<Record<string, BeaconInput[]>>,
  phArrivalInputs: Record<string, Record<number, string>>,
) {
  async function saveRow(userId: string, bIdx: number): Promise<void> {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return;

    const inputs = beaconInputs.value[userId];
    if (!inputs || !inputs[bIdx]) return;

    const beacon = comp.beacons[bIdx];
    const input = inputs[bIdx];

    const oldCode = (beacon.enteredCode || "").toUpperCase();
    const newTime = input.time.trim();
    const oldTime = formatIsoToHms(beacon.passageTime);

    const codeChanged = hasCodeChanged(input.code, beacon.enteredCode || "");
    const timeChanged = hasTimeChanged(input.time, oldTime);

    if (!codeChanged && !timeChanged) return;

    const codeToSend = codeChanged
      ? codeToPayload(input.code)
      : (oldCode.length === 2 ? oldCode : null);
    const passage_time = hmsToIsoTimestamp(newTime) || null;
    const creation_date = toLocalISO(new Date());

    const res = await apiFetch(
      `/api/events/${eventId}/registrations/${userId}/checkpoint-edit`,
      {
        method: "POST",
        body: JSON.stringify({ creation_date, passage_time, sequence: beacon.sequence, code: codeToSend }),
      },
    );

    if (res.ok) {
      beacon.enteredCode = codeToSend;
      beacon.passageTime = passage_time;
      beacon.valid = (beacon.expectedCode && codeToSend)
        ? codeToSend === beacon.expectedCode.toUpperCase()
        : null;

      comp.current_ph = computeCurrentPh(comp.beacons, comp.departed, comp.dns, comp.abandoned);

      inputs[bIdx] = {
        code: beacon.enteredCode || "",
        time: formatIsoToHms(beacon.passageTime),
      };
    }
  }

  async function savePhArrival(userId: string, bIdx: number): Promise<void> {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return;

    const beacon = comp.beacons[bIdx];
    if (!beacon.is_ph) return;

    const arrivalInputs = phArrivalInputs[userId];
    if (!arrivalInputs) return;

    const newTime = (arrivalInputs[beacon.sequence] || "").trim();
    const oldTime = formatIsoToHms(beacon.phArrivalTime);
    if (!hasTimeChanged(arrivalInputs[beacon.sequence] || "", oldTime)) return;

    const passage_time = hmsToIsoTimestamp(newTime) || null;
    const creation_date = toLocalISO(new Date());

    const res = await apiFetch(
      `/api/events/${eventId}/registrations/${userId}/ph-arrival-edit`,
      {
        method: "POST",
        body: JSON.stringify({ creation_date, passage_time, sequence: beacon.sequence }),
      },
    );

    if (res.ok) {
      beacon.phArrivalTime = passage_time;
      arrivalInputs[beacon.sequence] = formatIsoToHms(beacon.phArrivalTime);
    }
  }

  function fillCurrentTime(userId: string, bIdx: number): void {
    const inputs = beaconInputs.value[userId];
    if (inputs && inputs[bIdx]) {
      inputs[bIdx].time = formatTime(new Date());
    }
  }

  function fillPhArrivalCurrentTime(userId: string, bIdx: number): void {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return;
    const beacon = comp.beacons[bIdx];
    if (!beacon.is_ph) return;
    const arrivalInputs = phArrivalInputs[userId];
    if (arrivalInputs) {
      arrivalInputs[beacon.sequence] = formatTime(new Date());
    }
  }

  return { saveRow, savePhArrival, fillCurrentTime, fillPhArrivalCurrentTime };
}

