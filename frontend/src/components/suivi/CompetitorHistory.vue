<script setup lang="ts">
import type { LogEntry } from "../../types/log";

const props = defineProps<{ logs: LogEntry[] }>();

const ACTION_TYPES = [
  "checkpoint_edit",
  "abandon",
  "abandon_cancel",
  "tracker_returned",
  "tracker_returned_cancel",
];

function filteredLogs(): LogEntry[] {
  return props.logs.filter((log) => ACTION_TYPES.includes(log.log_type));
}

function formatEntry(log: LogEntry): string {
  switch (log.log_type) {
    case "checkpoint_edit": {
      const code = log.data?.code ? `"${log.data.code}"` : "—";
      const time = log.data?.passage_time
        ? (log.data.passage_time as string)
        : "—";
      return `Balise ${log.data?.sequence} → ${code} | ${time}`;
    }
    case "abandon":
      return `Abandon : ${log.data?.comment}`;
    case "abandon_cancel":
      return `Annulation abandon : ${log.data?.comment}`;
    case "tracker_returned":
      return `Tracker rendu (n°${log.data?.tracker_number})`;
    case "tracker_returned_cancel":
      return "Annulation rendu tracker";
    default:
      return log.log_type;
  }
}

function formatTimestamp(log: LogEntry): string {
  if (!log.metadata.creation_date) return "—";
  return log.metadata.creation_date.substring(11, 19);
}
</script>

<template>
  <div v-if="filteredLogs().length > 0" class="section-history">
    <h4>Historique</h4>
    <ul class="history-list">
      <li
        v-for="(entry, idx) in filteredLogs()"
        :key="idx"
        :title="`${formatTimestamp(entry)} — ${entry.metadata.author_name || entry.metadata.author_id.substring(0, 8)}…`"
      >
        <span class="history-time">{{ formatTimestamp(entry) }}</span>
        <span class="history-author">{{ entry.metadata.author_name || "?" }}</span>
        <span class="history-desc">{{ formatEntry(entry) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.section-history h4 {
  margin: 0 0 0.25rem;
  font-size: 0.85rem;
  color: #666;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.8rem;
}

.history-list li {
  padding: 0.2rem 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: default;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.history-time {
  color: #999;
  flex-shrink: 0;
}

.history-author {
  color: #999;
  flex-shrink: 0;
  font-weight: 600;
}

.history-desc {
  flex: 1;
}
</style>

