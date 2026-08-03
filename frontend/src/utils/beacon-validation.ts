const HMS_PATTERN = /^\d{2}:\d{2}:\d{2}$/;

/** A time value is saveable if it's empty (clearing) or valid HH:MM:SS */
export function isTimeValidForSave(time: string): boolean {
  return time.length === 0 || HMS_PATTERN.test(time);
}

/** A code value is saveable if it's empty (clearing) or exactly 2 chars */
export function isCodeValidForSave(code: string): boolean {
  return code.length === 0 || code.length === 2;
}

/** Determines if code has meaningfully changed and is valid for save */
export function hasCodeChanged(newCode: string, oldCode: string): boolean {
  const normalizedNew = newCode.toUpperCase().trim();
  const normalizedOld = oldCode.toUpperCase();
  return normalizedNew !== normalizedOld && isCodeValidForSave(normalizedNew);
}

/** Determines if time has meaningfully changed and is valid for save */
export function hasTimeChanged(newTime: string, oldTime: string): boolean {
  const trimmed = newTime.trim();
  return trimmed !== oldTime && isTimeValidForSave(trimmed);
}

/** Converts a code input to the API payload value (null if empty) */
export function codeToPayload(code: string): string | null {
  const normalized = code.toUpperCase().trim();
  return normalized.length === 2 ? normalized : null;
}

