import type { Course } from "../types/event";
import type { CompetitorBeacon, CheckpointState } from "../types/competitor";
import type { LogEntry } from "../types/log";
import { isoToHms } from "./date";

export function buildCompetitorBeacons(
  courseNumber: number | null,
  courses: Course[],
  checkpoints: Map<number, { code: string | null; passage_time: string | null }>,
  phArrivals?: Map<number, string>,
): CompetitorBeacon[] {
  if (!courseNumber) return [];

  const course = courses.find((c) => c.number === courseNumber);
  if (!course) return [];

  return course.beacons.map((beacon, index) => {
    const sequence = index + 1;
    const checkpoint = checkpoints.get(sequence);
    const enteredCode = checkpoint?.code || null;
    let valid: boolean | null = null;
    if (enteredCode && beacon.code) {
      valid = enteredCode.toUpperCase() === beacon.code.toUpperCase();
    }

    return {
      sequence,
      beaconNumber: beacon.number,
      tag: beacon.tag,
      is_ph: beacon.is_ph,
      expectedCode: beacon.code,
      enteredCode,
      valid,
      passageTime: checkpoint?.passage_time || null,
      phArrivalTime: beacon.is_ph ? (phArrivals?.get(sequence) || null) : null,
    };
  });
}

export function computeCurrentPh(
  competitorBeacons: CompetitorBeacon[],
  departed: boolean,
  dns: boolean,
  abandoned: boolean,
): string | null {
  if (dns || abandoned || !departed) return null;

  const phBeacons = competitorBeacons.filter((b) => b.is_ph);
  let lastPassedPhIndex = -1;

  for (let i = 0; i < phBeacons.length; i++) {
    if (phBeacons[i].passageTime) {
      lastPassedPhIndex = i;
    }
  }

  if (lastPassedPhIndex === phBeacons.length - 1) {
    return "Arrivé";
  }

  const nextPhIndex = lastPassedPhIndex + 1;
  return `PH${nextPhIndex + 1}`;
}

export function reconstructTrackingState(
  reg: Record<string, unknown>,
  logs: LogEntry[],
  checkpoints: CheckpointState[],
  courses: Course[],
  phArrivalsRaw?: Record<string, string>,
): {
  departed: boolean;
  departureTime: string | null;
  dns: boolean;
  abandoned: boolean;
  trackerReturned: boolean;
  competitorBeacons: CompetitorBeacon[];
  currentPh: string | null;
} {
  let departed = false;
  let departureTime: string | null = null;
  let dns = false;
  let abandoned = false;
  let trackerReturned = false;

  for (const log of logs) {
    switch (log.log_type) {
      case "departure":
        departed = true;
        departureTime = isoToHms(log.metadata.creation_date);
        break;
      case "departure_cancel":
        departed = false;
        departureTime = null;
        break;
      case "dns":
        dns = true;
        break;
      case "dns_cancel":
        dns = false;
        break;
      case "abandon":
        abandoned = true;
        break;
      case "abandon_cancel":
        abandoned = false;
        break;
      case "tracker_returned":
        trackerReturned = true;
        break;
      case "tracker_returned_cancel":
        trackerReturned = false;
        break;
    }
  }

  const courseNumber = reg.course_number as number | null;
  const checkpointMap = new Map<number, { code: string | null; passage_time: string | null }>();
  for (const cp of checkpoints) {
    checkpointMap.set(cp.sequence, { code: cp.code, passage_time: cp.passage_time });
  }

  const phArrivals = new Map<number, string>();
  if (phArrivalsRaw) {
    for (const [key, val] of Object.entries(phArrivalsRaw)) {
      phArrivals.set(Number(key), val);
    }
  }

  const competitorBeacons = buildCompetitorBeacons(courseNumber, courses, checkpointMap, phArrivals);
  const currentPh = computeCurrentPh(competitorBeacons, departed, dns, abandoned);

  return { departed, departureTime, dns, abandoned, trackerReturned, competitorBeacons, currentPh };
}

