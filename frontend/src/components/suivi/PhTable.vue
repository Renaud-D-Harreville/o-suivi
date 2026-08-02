<script setup lang="ts">
import { formatMinutes } from "../../utils/date";

export interface PhRow {
  gate: string;
  min: number | null;
  max: number | null;
  elapsed: number | null;
  status: "passed" | "current" | "future";
  colorClass: string;
}

defineProps<{ rows: PhRow[] }>();
</script>

<template>
  <div v-if="rows.length > 0" class="section-ph">
    <table class="ph-table">
      <thead>
        <tr>
          <th>PH</th>
          <th>Tps min</th>
          <th>Tps max</th>
          <th>Tps écoulé</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.gate"
          :class="['ph-row', `ph-${row.status}`]"
        >
          <td>{{ row.gate }}</td>
          <td>{{ formatMinutes(row.min) }}</td>
          <td>{{ formatMinutes(row.max) }}</td>
          <td :class="row.colorClass">{{ formatMinutes(row.elapsed) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.ph-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.ph-table th,
.ph-table td {
  padding: 0.35rem 0.5rem;
  border: 1px solid #e0e0e0;
  text-align: center;
}

.ph-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.ph-row.ph-passed { background: #f5f5f5; }
.ph-row.ph-current { background: #fff; }
.ph-row.ph-future { background: #fff; }

.elapsed-black { color: #333; }
.elapsed-green { color: #4caf50; font-weight: 700; }
.elapsed-red { color: #f44336; font-weight: 700; }
</style>

