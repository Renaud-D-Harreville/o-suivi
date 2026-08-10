import { describe, it, expect } from "vitest";
import {
  formatDuration,
  formatResultTime,
  formatDelay,
  globalIcon,
  sectionIcon,
  beaconIcon,
} from "../format";

describe("formatDuration", () => {
  it("returns - for null", () => {
    expect(formatDuration(null)).toBe("-");
  });

  it("formats zero seconds", () => {
    expect(formatDuration(0)).toBe("0′00″");
  });

  it("formats seconds under a minute", () => {
    expect(formatDuration(45)).toBe("0′45″");
  });

  it("formats minutes + seconds", () => {
    expect(formatDuration(125)).toBe("2′05″");
  });

  it("formats hours + minutes + seconds", () => {
    expect(formatDuration(3661)).toBe("1h01′01″");
  });

  it("formats negative values", () => {
    expect(formatDuration(-90)).toBe("-1′30″");
  });
});

describe("formatResultTime", () => {
  it("returns - for null", () => {
    expect(formatResultTime(null)).toBe("-");
  });

  it("returns HH:MM from HH:MM:SS input", () => {
    expect(formatResultTime("09:30:15")).toBe("09:30");
  });

  it("returns HH:MM from ISO input (backward compat)", () => {
    expect(formatResultTime("2026-08-05T09:30:15")).toBe("09:30");
  });
});

describe("formatDelay", () => {
  it("returns empty string for null", () => {
    expect(formatDelay(null)).toBe("");
  });

  it("returns negative for early", () => {
    expect(formatDelay(-5)).toBe("-5 min");
  });

  it("returns positive with + for late", () => {
    expect(formatDelay(10)).toBe("+10 min");
  });

  it("returns empty string for zero", () => {
    expect(formatDelay(0)).toBe("");
  });
});

describe("globalIcon", () => {
  it("returns empty for DNS", () => {
    expect(globalIcon(true, null)).toBe("");
  });

  it("returns ✅ for valid", () => {
    expect(globalIcon(false, true)).toBe("✅");
  });

  it("returns ❌ for invalid", () => {
    expect(globalIcon(false, false)).toBe("❌");
  });

  it("returns ⏳ for null/pending", () => {
    expect(globalIcon(false, null)).toBe("⏳");
  });
});

describe("sectionIcon", () => {
  it("returns ✅ for true", () => {
    expect(sectionIcon(true)).toBe("✅");
  });

  it("returns ❌ for false", () => {
    expect(sectionIcon(false)).toBe("❌");
  });

  it("returns - for null", () => {
    expect(sectionIcon(null)).toBe("-");
  });
});

describe("beaconIcon", () => {
  it("returns ✅ for true", () => {
    expect(beaconIcon(true)).toBe("✅");
  });

  it("returns ❌ for false", () => {
    expect(beaconIcon(false)).toBe("❌");
  });

  it("returns - for null", () => {
    expect(beaconIcon(null)).toBe("-");
  });
});

