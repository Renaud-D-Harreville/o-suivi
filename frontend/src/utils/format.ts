export function shortName(firstName: string, lastName: string): string {
  const initial = lastName ? `${lastName.charAt(0).toUpperCase()}.` : "";
  return initial ? `${firstName} ${initial}` : firstName;
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return "-";
  const sign = seconds < 0 ? "-" : "";
  const abs = Math.abs(seconds);
  const h = Math.floor(abs / 3600);
  const m = Math.floor((abs % 3600) / 60);
  const s = abs % 60;
  if (h > 0) {
    return `${sign}${h}h${String(m).padStart(2, "0")}′${String(s).padStart(2, "0")}″`;
  }
  return `${sign}${m}′${String(s).padStart(2, "0")}″`;
}

export function formatResultTime(timeString: string | null): string {
  if (!timeString) return "-";
  // Already HH:MM:SS — return HH:MM
  if (!timeString.includes("T")) return timeString.substring(0, 5);
  // ISO fallback — extract HH:MM
  return timeString.substring(11, 16);
}

export function formatDelay(minutes: number | null): string {
  if (minutes === null || minutes === undefined) return "";
  if (minutes < 0) return `${minutes} min`;
  if (minutes > 0) return `+${minutes} min`;
  return "";
}

export function globalIcon(dns: boolean, validGlobal: boolean | null): string {
  if (dns) return "";
  if (validGlobal === true) return "✅";
  if (validGlobal === false) return "❌";
  return "⏳";
}

export function sectionIcon(valid: boolean | null): string {
  if (valid === true) return "✅";
  if (valid === false) return "❌";
  return "-";
}

export function beaconIcon(valid: boolean | null): string {
  if (valid === true) return "✅";
  if (valid === false) return "❌";
  return "-";
}
