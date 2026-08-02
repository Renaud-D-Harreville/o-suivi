export interface BeaconResult {
  sequence: number;
  beacon_number: number;
  tag: string;
  gate: string | null;
  expected_code: string | null;
  entered_code: string | null;
  valid: boolean | null;
  split_time: number | null;
  cumulated_section_time: number | null;
}

export interface SectionResult {
  gate: string;
  valid: boolean | null;
  delay: number | null;
  section_time: number | null;
  running_time: number | null;
  pause_time: number | null;
}

export interface CompetitorResult {
  user_id: string;
  first_name: string;
  last_name: string;
  sex: string | null;
  course_number: number | null;
  valid_global: boolean | null;
  dns: boolean;
  abandoned: boolean;
  bag_weight_start: number | null;
  bag_weight_end: number | null;
  departure_time: string | null;
  arrival_time: string | null;
  total_time: number | null;
  total_running_time: number | null;
  sections: SectionResult[];
  beacons: BeaconResult[];
}

export interface PublicCompetitorResult extends CompetitorResult {
  finished: boolean;
  has_tracker: boolean;
  tracker_returned: boolean;
}

export interface ResultsData {
  routechoices_url: string | null;
  competitors: CompetitorResult[];
}

export interface PublicResultsData {
  routechoices_url: string | null;
  public_routechoices_time: string | null;
  event_date: string | null;
  competitors: PublicCompetitorResult[];
}

export interface TemplateSummary {
  id: string;
  name: string;
}

export interface EventSummary {
  id: string;
  name: string;
  date: string | null;
}

