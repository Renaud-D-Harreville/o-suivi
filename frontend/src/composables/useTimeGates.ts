import type { Ref } from "vue";
import type { TimeGates, TimeGateEntry } from "../types/event";
import type { TrackingCompetitor } from "../types/competitor";
import { formatSecondsToHms, formatTime, secondsBetween } from "../utils/date";

export function useTimeGates(
  allTimeGates: Ref<TimeGates[]>,
  currentTime: Ref<Date>,
) {
  function getGatesForCompetitor(comp: TrackingCompetitor): TimeGateEntry[] {
    if (!comp.course_number) return [];
    const tg = allTimeGates.value.find((t) => t.course_number === comp.course_number);
    return tg?.gates || [];
  }

  function getElapsedMinutes(comp: TrackingCompetitor, gateIndex: number): number | null {
    if (!comp.departed || !comp.departure_time) return null;

    const gates = getGatesForCompetitor(comp);
    if (gateIndex >= gates.length) return null;

    const phBeacons = comp.beacons.filter((b) => b.is_ph);

    let sectionStart: string;
    if (gateIndex === 0) {
      sectionStart = comp.departure_time;
    } else {
      const prevPhBeacon = phBeacons[gateIndex - 1];
      if (!prevPhBeacon?.passageTime) return null;
      sectionStart = prevPhBeacon.passageTime;
    }

    const currentPhBeacon = phBeacons[gateIndex];
    if (currentPhBeacon?.passageTime) {
      const secs = secondsBetween(sectionStart, currentPhBeacon.passageTime);
      return secs !== null ? Math.round(secs / 60) : null;
    }

    const currentPhLabel = `PH${gateIndex + 1}`;
    if (comp.current_ph === currentPhLabel) {
      const secs = secondsBetween(sectionStart, formatTime(currentTime.value));
      return secs !== null ? Math.round(secs / 60) : null;
    }

    return null;
  }

  function getStatus(
    comp: TrackingCompetitor,
    gateIndex: number,
  ): "passed" | "current" | "future" {
    const gates = getGatesForCompetitor(comp);
    if (gateIndex >= gates.length) return "future";

    if (comp.current_ph === "Arrivé") return "passed";
    if (!comp.current_ph) return "future";

    const gateNames = gates.map((g) => g.gate);
    const currentIdx = gateNames.indexOf(comp.current_ph);

    if (gateIndex < currentIdx) return "passed";
    if (gateIndex === currentIdx) return "current";
    return "future";
  }

  function getElapsedColor(
    comp: TrackingCompetitor,
    gateIndex: number,
    elapsed: number | null,
  ): string {
    if (elapsed === null) return "";

    const gates = getGatesForCompetitor(comp);
    if (gateIndex >= gates.length) return "";

    const gate = gates[gateIndex];
    const min = comp.sex === "F" ? gate.min_f : gate.min_m;
    const max = comp.sex === "F" ? gate.max_f : gate.max_m;

    if (max !== null && elapsed > max) return "elapsed-red";
    if (min !== null && elapsed >= min) return "elapsed-green";
    return "elapsed-black";
  }

  function getElapsedSinceLastPh(comp: TrackingCompetitor): string {
    if (!comp.departed || !comp.departure_time || comp.dns || comp.abandoned) return "";
    if (comp.current_ph === "Arrivé") return "";

    const phBeacons = comp.beacons.filter((b) => b.is_ph);
    let lastTime = comp.departure_time;

    for (const phBeacon of phBeacons) {
      if (phBeacon.passageTime) {
        lastTime = phBeacon.passageTime;
      } else {
        break;
      }
    }

    const secs = secondsBetween(lastTime, formatTime(currentTime.value));
    if (secs === null || secs < 0) return "00:00:00";
    return formatSecondsToHms(secs);
  }

  function getRowClass(comp: TrackingCompetitor): string {
    if (comp.dns) return "row-dns";
    if (comp.abandoned) return "row-abandon";
    if (comp.current_ph === "Arrivé" && comp.tracker_returned) return "row-arrived";
    if (!comp.departed) return "row-default";

    const gates = getGatesForCompetitor(comp);
    if (comp.current_ph && comp.current_ph !== "Arrivé") {
      const gateIndex = gates.findIndex((g) => g.gate === comp.current_ph);
      if (gateIndex >= 0) {
        const elapsed = getElapsedMinutes(comp, gateIndex);
        const gate = gates[gateIndex];
        const max = comp.sex === "F" ? gate.max_f : gate.max_m;
        if (elapsed !== null && max !== null && elapsed > max) return "row-late";
      }
    }

    return "row-default";
  }

  return {
    getGatesForCompetitor,
    getElapsedMinutes,
    getStatus,
    getElapsedColor,
    getElapsedSinceLastPh,
    getRowClass,
  };
}

