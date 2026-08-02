export interface LogMetadata {
  creation_date: string;
  received_at: string;
  author_id: string;
  author_name: string;
}

export interface LogEntry {
  log_type: string;
  metadata: LogMetadata;
  data?: Record<string, unknown>;
}

export interface BeaconInput {
  code: string;
  time: string;
}

