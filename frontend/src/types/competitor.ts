import type { LogEntry } from "./log";

export interface CheckpointState {
  sequence: number;
  code: string | null;
  passage_time: string | null;
}

export interface CompetitorBeacon {
  sequence: number;
  beaconNumber: number;
  tag: string;
  is_ph: boolean;
  expectedCode: string | null;
  enteredCode: string | null;
  valid: boolean | null;
  passageTime: string | null;
  phArrivalTime: string | null;
}

export interface TrackingCompetitor {
  user_id: string;
  first_name: string;
  last_name: string;
  sex: string;
  phone: string;
  course_number: number | null;
  start_order: number | null;
  start_time_planned: string | null;
  tracker_number: string | null;
  departed: boolean;
  departure_time: string | null;
  dns: boolean;
  abandoned: boolean;
  tracker_returned: boolean;
  bag_weight_start: number | null;
  current_ph: string | null;
  beacons: CompetitorBeacon[];
  logs: LogEntry[];
}


