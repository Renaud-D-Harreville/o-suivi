export interface Beacon {
  id: number;
  number: number;
  tag: string;
  is_ph: boolean;
  code: string | null;
}

export interface Course {
  number: number;
  beacons: Beacon[];
}

export interface TimeGateEntry {
  gate: string;
  min_m: number | null;
  max_m: number | null;
  min_f: number | null;
  max_f: number | null;
}

export interface TimeGates {
  course_number: number;
  gates: TimeGateEntry[];
}

