import { describe, it, expect } from "vitest";
import {
  toLocalISO,
  formatTime,
  formatSecondsToHms,
  formatMinutes,
  secondsBetween,
  isoToHms,
} from "../date";

describe("toLocalISO", () => {
  it("formats a date to local ISO string without timezone", () => {
    const date = new Date(2026, 6, 15, 8, 30, 45); // July 15, 2026 08:30:45
    const result = toLocalISO(date);
    expect(result).toBe("2026-07-15T08:30:45");
  });

  it("pads single-digit month and day", () => {
    const date = new Date(2026, 0, 5, 3, 4, 7); // Jan 5, 2026 03:04:07
    const result = toLocalISO(date);
    expect(result).toBe("2026-01-05T03:04:07");
  });
});

describe("formatTime", () => {
  it("formats a date as HH:MM:SS in fr-FR locale", () => {
    const result = formatTime(new Date(2026, 0, 1, 14, 30, 0));
    expect(result).toMatch(/14:30:00/);
  });
});

describe("formatSecondsToHms", () => {
  it("formats 0 seconds", () => {
    expect(formatSecondsToHms(0)).toBe("00:00:00");
  });

  it("formats seconds correctly", () => {
    expect(formatSecondsToHms(3661)).toBe("01:01:01");
  });

  it("formats large values", () => {
    expect(formatSecondsToHms(36000)).toBe("10:00:00");
  });

  it("formats sub-minute values", () => {
    expect(formatSecondsToHms(45)).toBe("00:00:45");
  });
});

describe("secondsBetween", () => {
  it("returns difference in seconds for valid HH:MM:SS inputs", () => {
    expect(secondsBetween("09:00:00", "10:30:00")).toBe(5400);
  });

  it("returns negative for reversed times", () => {
    expect(secondsBetween("10:00:00", "09:00:00")).toBe(-3600);
  });

  it("returns null for null start", () => {
    expect(secondsBetween(null, "10:00:00")).toBeNull();
  });

  it("returns null for null end", () => {
    expect(secondsBetween("09:00:00", null)).toBeNull();
  });

  it("returns null for empty strings", () => {
    expect(secondsBetween("", "10:00:00")).toBeNull();
  });

  it("handles HH:MM without seconds", () => {
    expect(secondsBetween("09:00", "10:00")).toBe(3600);
  });
});

describe("isoToHms", () => {
  it("extracts HH:MM:SS from ISO timestamp", () => {
    expect(isoToHms("2026-07-15T08:30:45")).toBe("08:30:45");
  });

  it("returns the value if already HH:MM:SS", () => {
    expect(isoToHms("08:30:45")).toBe("08:30:45");
  });

  it("returns empty string for empty input", () => {
    expect(isoToHms("")).toBe("");
  });
});

describe("formatMinutes", () => {
  it("returns --- for null", () => {
    expect(formatMinutes(null)).toBe("---");
  });

  it("formats 0 minutes", () => {
    expect(formatMinutes(0)).toBe("0h00");
  });

  it("formats minutes less than 60", () => {
    expect(formatMinutes(45)).toBe("0h45");
  });

  it("formats exact hours", () => {
    expect(formatMinutes(120)).toBe("2h00");
  });

  it("formats hours + minutes", () => {
    expect(formatMinutes(90)).toBe("1h30");
  });

  it("formats single-digit minutes with padding", () => {
    expect(formatMinutes(65)).toBe("1h05");
  });
});

