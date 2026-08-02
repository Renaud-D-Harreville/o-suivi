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

export function hmsToIsoTimestamp(hms: string): string | null {
  const match = hms.match(/^(\d{2}):(\d{2}):(\d{2})$/);
  if (!match) return null;
  const now = new Date();
  const date = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")}`;
  return `${date}T${hms}`;
}

export function formatIsoToHms(isoTimestamp: string | null): string {
  if (!isoTimestamp) return "";
  return isoTimestamp.substring(11, 19);
}

export function formatMinutes(minutes: number | null): string {
  if (minutes === null) return "---";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h${m.toString().padStart(2, "0")}`;
}


