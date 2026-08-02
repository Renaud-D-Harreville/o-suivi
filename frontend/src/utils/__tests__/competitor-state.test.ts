import { describe, it, expect } from "vitest";
import { buildCompetitorBeacons, computeCurrentPh } from "../competitor-state";
import type { Course } from "../../types/event";
import type { CompetitorBeacon } from "../../types/competitor";

const baseCourse: Course = {
  number: 1,
  beacons: [
    { id: 1, number: 1, tag: "unique", is_ph: false, code: "AB" },
    { id: 2, number: 2, tag: "unique", is_ph: true, code: "CD" },
    { id: 3, number: 3, tag: "unique", is_ph: false, code: "EF" },
    { id: 4, number: 4, tag: "unique", is_ph: true, code: "GH" },
  ],
};

describe("buildCompetitorBeacons", () => {
  it("returns empty array when courseNumber is null", () => {
    const result = buildCompetitorBeacons(null, [baseCourse], new Map());
    expect(result).toEqual([]);
  });

  it("returns empty array when course not found", () => {
    const result = buildCompetitorBeacons(99, [baseCourse], new Map());
    expect(result).toEqual([]);
  });

  it("builds beacons from course with no checkpoints", () => {
    const result = buildCompetitorBeacons(1, [baseCourse], new Map());
    expect(result).toHaveLength(4);
    expect(result[0].sequence).toBe(1);
    expect(result[0].beaconNumber).toBe(1);
    expect(result[0].is_ph).toBe(false);
    expect(result[0].expectedCode).toBe("AB");
    expect(result[0].enteredCode).toBeNull();
    expect(result[0].valid).toBeNull();
    expect(result[0].passageTime).toBeNull();
  });

  it("fills in checkpoint data when available", () => {
    const checkpoints = new Map<number, { code: string | null; passage_time: string | null }>();
    checkpoints.set(1, { code: "AB", passage_time: "2026-07-15T08:30:00" });
    checkpoints.set(2, { code: "XX", passage_time: "2026-07-15T09:00:00" });

    const result = buildCompetitorBeacons(1, [baseCourse], checkpoints);
    expect(result[0].enteredCode).toBe("AB");
    expect(result[0].valid).toBe(true);
    expect(result[0].passageTime).toBe("2026-07-15T08:30:00");

    expect(result[1].enteredCode).toBe("XX");
    expect(result[1].valid).toBe(false); // XX !== CD
  });

  it("fills PH arrival times when provided", () => {
    const phArrivals = new Map<number, string>();
    phArrivals.set(2, "2026-07-15T08:55:00");

    const result = buildCompetitorBeacons(1, [baseCourse], new Map(), phArrivals);
    expect(result[1].phArrivalTime).toBe("2026-07-15T08:55:00");
    expect(result[0].phArrivalTime).toBeNull(); // not a PH beacon
  });
});

describe("computeCurrentPh", () => {
  function makeBeacons(overrides?: Partial<CompetitorBeacon>[]): CompetitorBeacon[] {
    const defaults: CompetitorBeacon[] = [
      { sequence: 1, beaconNumber: 1, tag: "unique", is_ph: false, expectedCode: "AB", enteredCode: null, valid: null, passageTime: null, phArrivalTime: null },
      { sequence: 2, beaconNumber: 2, tag: "unique", is_ph: true, expectedCode: "CD", enteredCode: null, valid: null, passageTime: null, phArrivalTime: null },
      { sequence: 3, beaconNumber: 3, tag: "unique", is_ph: false, expectedCode: "EF", enteredCode: null, valid: null, passageTime: null, phArrivalTime: null },
      { sequence: 4, beaconNumber: 4, tag: "unique", is_ph: true, expectedCode: "GH", enteredCode: null, valid: null, passageTime: null, phArrivalTime: null },
    ];
    if (overrides) {
      overrides.forEach((o, i) => {
        defaults[i] = { ...defaults[i], ...o };
      });
    }
    return defaults;
  }

  it("returns null when not departed", () => {
    expect(computeCurrentPh(makeBeacons(), false, false, false)).toBeNull();
  });

  it("returns null when DNS", () => {
    expect(computeCurrentPh(makeBeacons(), true, true, false)).toBeNull();
  });

  it("returns null when abandoned", () => {
    expect(computeCurrentPh(makeBeacons(), true, false, true)).toBeNull();
  });

  it("returns PH1 when departed but no PH passed", () => {
    expect(computeCurrentPh(makeBeacons(), true, false, false)).toBe("PH1");
  });

  it("returns PH2 when first PH passed", () => {
    const beacons = makeBeacons([
      {},
      { passageTime: "2026-07-15T09:00:00" },
    ]);
    expect(computeCurrentPh(beacons, true, false, false)).toBe("PH2");
  });

  it("returns Arrivé when all PHs passed", () => {
    const beacons = makeBeacons([
      {},
      { passageTime: "2026-07-15T09:00:00" },
      {},
      { passageTime: "2026-07-15T10:00:00" },
    ]);
    expect(computeCurrentPh(beacons, true, false, false)).toBe("Arrivé");
  });
});

