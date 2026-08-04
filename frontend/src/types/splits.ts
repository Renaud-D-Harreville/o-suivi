export interface SplitEntry {
  user_id: string;
  split_seconds: number;
}

export interface BeaconPairSplits {
  from_beacon_id: number | null;
  to_beacon_id: number;
  splits: SplitEntry[];
}

export interface CompetitorSummary {
  user_id: string;
  first_name: string;
  last_name: string;
  sex: string | null;
  course_number: number | null;
}

export interface EventBeaconInfo {
  id: number;
  number: number;
  tag: string;
  is_ph: boolean;
  code: string;
}

export interface SplitsResponse {
  event_name: string;
  beacons: EventBeaconInfo[];
  competitors: CompetitorSummary[];
  pairs: BeaconPairSplits[];
}

