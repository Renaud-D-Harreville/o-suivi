import { describe, it, expect } from "vitest";
import {
  isTimeValidForSave,
  isCodeValidForSave,
  hasCodeChanged,
  hasTimeChanged,
  codeToPayload,
} from "../beacon-validation";

describe("isTimeValidForSave", () => {
  it("returns true for empty string (clearing time)", () => {
    expect(isTimeValidForSave("")).toBe(true);
  });

  it("returns true for valid HH:MM:SS format", () => {
    expect(isTimeValidForSave("08:30:00")).toBe(true);
    expect(isTimeValidForSave("23:59:59")).toBe(true);
    expect(isTimeValidForSave("00:00:00")).toBe(true);
  });

  it("returns false for partial time input", () => {
    expect(isTimeValidForSave("08:3")).toBe(false);
    expect(isTimeValidForSave("08:30")).toBe(false);
    expect(isTimeValidForSave("08:30:0")).toBe(false);
  });

  it("returns false for invalid format with correct length", () => {
    expect(isTimeValidForSave("ab:cd:ef")).toBe(false);
    expect(isTimeValidForSave("12-30-00")).toBe(false);
    expect(isTimeValidForSave("1:30:000")).toBe(false);
  });
});

describe("isCodeValidForSave", () => {
  it("returns true for empty string (clearing code)", () => {
    expect(isCodeValidForSave("")).toBe(true);
  });

  it("returns true for 2-character code", () => {
    expect(isCodeValidForSave("AB")).toBe(true);
    expect(isCodeValidForSave("xy")).toBe(true);
  });

  it("returns false for 1-character code", () => {
    expect(isCodeValidForSave("A")).toBe(false);
  });

  it("returns false for 3+ character code", () => {
    expect(isCodeValidForSave("ABC")).toBe(false);
  });
});

describe("hasCodeChanged", () => {
  it("returns true when code changed to a valid value", () => {
    expect(hasCodeChanged("AB", "")).toBe(true);
    expect(hasCodeChanged("AB", "CD")).toBe(true);
  });

  it("returns true when code is cleared", () => {
    expect(hasCodeChanged("", "AB")).toBe(true);
  });

  it("returns false when code is the same (case-insensitive)", () => {
    expect(hasCodeChanged("ab", "AB")).toBe(false);
    expect(hasCodeChanged("AB", "AB")).toBe(false);
  });

  it("returns false when code is invalid length", () => {
    expect(hasCodeChanged("A", "AB")).toBe(false);
    expect(hasCodeChanged("ABC", "AB")).toBe(false);
  });

  it("handles whitespace trimming", () => {
    expect(hasCodeChanged(" AB ", "AB")).toBe(false);
    expect(hasCodeChanged(" CD ", "AB")).toBe(true);
  });
});

describe("hasTimeChanged", () => {
  it("returns true when time changed to valid HH:MM:SS", () => {
    expect(hasTimeChanged("09:00:00", "08:30:00")).toBe(true);
  });

  it("returns true when time is cleared (empty)", () => {
    expect(hasTimeChanged("", "08:30:00")).toBe(true);
  });

  it("returns false when time is the same", () => {
    expect(hasTimeChanged("08:30:00", "08:30:00")).toBe(false);
  });

  it("returns false when new time is invalid format", () => {
    expect(hasTimeChanged("08:3", "08:30:00")).toBe(false);
    expect(hasTimeChanged("abc", "08:30:00")).toBe(false);
    expect(hasTimeChanged("ab:cd:ef", "08:30:00")).toBe(false);
  });

  it("returns false when both are empty (no change)", () => {
    expect(hasTimeChanged("", "")).toBe(false);
  });

  it("handles whitespace trimming", () => {
    expect(hasTimeChanged(" 08:30:00 ", "08:30:00")).toBe(false);
    expect(hasTimeChanged(" 09:00:00 ", "08:30:00")).toBe(true);
  });
});

describe("codeToPayload", () => {
  it("returns uppercase 2-char code", () => {
    expect(codeToPayload("ab")).toBe("AB");
    expect(codeToPayload("CD")).toBe("CD");
  });

  it("returns null for empty code", () => {
    expect(codeToPayload("")).toBeNull();
  });

  it("returns null for single char", () => {
    expect(codeToPayload("A")).toBeNull();
  });

  it("trims whitespace before evaluating", () => {
    expect(codeToPayload(" AB ")).toBe("AB");
    expect(codeToPayload("  ")).toBeNull();
  });
});

