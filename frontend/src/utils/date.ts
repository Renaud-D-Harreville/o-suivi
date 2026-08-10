export function toLocalISO(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export function formatTime(date: Date): string {
  return date.toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function formatSecondsToHms(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function formatMinutes(minutes: number | null): string {
  if (minutes === null) return "---";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h${m.toString().padStart(2, "0")}`;
}

/**
 * Convert HH:MM:SS string to total seconds since midnight.
 */
function hmsToSeconds(hms: string): number | null {
  const parts = hms.split(":");
  if (parts.length < 2) return null;
  const h = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10);
  const s = parts.length > 2 ? parseInt(parts[2], 10) : 0;
  if (isNaN(h) || isNaN(m) || isNaN(s)) return null;
  return h * 3600 + m * 60 + s;
}

/**
 * Return seconds between two HH:MM:SS strings.
 * Returns null if either input is missing or invalid.
 */
export function secondsBetween(start: string | null, end: string | null): number | null {
  if (!start || !end) return null;
  const startSecs = hmsToSeconds(start);
  const endSecs = hmsToSeconds(end);
  if (startSecs === null || endSecs === null) return null;
  return endSecs - startSecs;
}

/**
 * Extract HH:MM:SS from an ISO timestamp (backward compat for log metadata).
 */
export function isoToHms(iso: string): string {
  if (!iso) return "";
  if (iso.includes("T")) return iso.split("T")[1].substring(0, 8);
  return iso.substring(0, 8);
}
