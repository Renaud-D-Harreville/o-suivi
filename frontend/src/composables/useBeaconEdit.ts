import { ref, reactive, type Ref } from "vue";
import type { TrackingCompetitor } from "../types/competitor";
import type { BeaconInput } from "../types/log";
import { hasCodeChanged, hasTimeChanged } from "../utils/beacon-validation";
import { useBeaconSave } from "./useBeaconSave";

export function useBeaconEdit(
  eventId: string,
  competitors: Ref<TrackingCompetitor[]>,
) {
  const beaconInputs = ref<Record<string, BeaconInput[]>>({});
  const phArrivalInputs = reactive<Record<string, Record<number, string>>>({});
  const savingRow = ref<{ userId: string; bIdx: number } | null>(null);

  const { saveRow: doSave, savePhArrival: doSavePhArrival, fillCurrentTime, fillPhArrivalCurrentTime } =
    useBeaconSave(eventId, competitors, beaconInputs, phArrivalInputs);

  function initInputs(comp: TrackingCompetitor): void {
    beaconInputs.value[comp.user_id] = comp.beacons.map((b) => ({
      code: b.enteredCode || "",
      time: b.passageTime || "",
    }));
    const arrivals: Record<number, string> = {};
    for (const b of comp.beacons) {
      if (b.is_ph) {
        arrivals[b.sequence] = b.phArrivalTime || "";
      }
    }
    phArrivalInputs[comp.user_id] = arrivals;
  }

  function syncInputs(comp: TrackingCompetitor): void {
    const existing = beaconInputs.value[comp.user_id];
    if (!existing || !existing.length) {
      initInputs(comp);
      return;
    }

    const newInputs = comp.beacons.map((b) => ({
      code: b.enteredCode || "",
      time: b.passageTime || "",
    }));
    beaconInputs.value[comp.user_id] = newInputs;

    const arrivals: Record<number, string> = {};
    for (const b of comp.beacons) {
      if (b.is_ph) {
        arrivals[b.sequence] = b.phArrivalTime || "";
      }
    }
    phArrivalInputs[comp.user_id] = arrivals;
  }

  function resetRow(userId: string, bIdx: number): void {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return;
    const beacon = comp.beacons[bIdx];
    const inputs = beaconInputs.value[userId];
    if (inputs && inputs[bIdx]) {
      inputs[bIdx] = {
        code: beacon.enteredCode || "",
        time: beacon.passageTime || "",
      };
    }
  }

  function resetPhArrival(userId: string, bIdx: number): void {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return;
    const beacon = comp.beacons[bIdx];
    if (!beacon.is_ph) return;
    const arrivalInputs = phArrivalInputs[userId];
    if (arrivalInputs) {
      arrivalInputs[beacon.sequence] = beacon.phArrivalTime || "";
    }
  }

  function getInputs(userId: string): BeaconInput[] {
    return beaconInputs.value[userId] || [];
  }

  function getPhArrivalInputs(userId: string): Record<number, string> {
    return phArrivalInputs[userId] || {};
  }

  function hasChanged(userId: string, bIdx: number): boolean {
    const comp = competitors.value.find((c) => c.user_id === userId);
    if (!comp) return false;

    const inputs = beaconInputs.value[userId];
    if (!inputs || !inputs[bIdx]) return false;

    const beacon = comp.beacons[bIdx];
    const input = inputs[bIdx];

    if (hasCodeChanged(input.code, beacon.enteredCode || "")) return true;

    return hasTimeChanged(input.time, beacon.passageTime || "");
  }

  async function saveRow(userId: string, bIdx: number): Promise<void> {
    savingRow.value = { userId, bIdx };
    try {
      await doSave(userId, bIdx);
    } finally {
      savingRow.value = null;
    }
  }

  async function savePhArrival(userId: string, bIdx: number): Promise<void> {
    savingRow.value = { userId, bIdx };
    try {
      await doSavePhArrival(userId, bIdx);
    } finally {
      savingRow.value = null;
    }
  }


  return { beaconInputs, phArrivalInputs, savingRow, initInputs, syncInputs, getInputs, getPhArrivalInputs, hasChanged, saveRow, savePhArrival, fillCurrentTime, fillPhArrivalCurrentTime, resetRow, resetPhArrival };
}
