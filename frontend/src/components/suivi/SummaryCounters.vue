<script setup lang="ts">
import { computed } from "vue";
import type { TrackingCompetitor } from "../../types/competitor";
import type { TimeGates, TimeGateEntry } from "../../types/event";

const props = defineProps<{
  competitors: TrackingCompetitor[];
  allTimeGates: TimeGates[];
}>();

function getGatesForCompetitor(comp: TrackingCompetitor): TimeGateEntry[] {
  if (!comp.course_number) return [];
  const tg = props.allTimeGates.find((t) => t.course_number === comp.course_number);
  return tg?.gates || [];
}

const counters = computed(() => {
  const all = props.competitors;
  const waiting = all.filter((c) => !c.departed && !c.dns).length;
  const departed = all.filter((c) => c.departed && !c.dns && !c.abandoned);
  const arrived = all.filter((c) => c.current_ph === "Arrivé");
  const dnsCount = all.filter((c) => c.dns).length;
  const abandonCount = all.filter((c) => c.abandoned).length;
  const inCourse = departed.length - arrived.length - abandonCount;

  const maxGates = Math.max(...props.allTimeGates.map((tg) => tg.gates.length), 0);
  const sections: number[] = Array(maxGates).fill(0);
  for (const comp of all) {
    if (comp.dns || comp.abandoned || !comp.departed || comp.current_ph === "Arrivé") continue;
    const gates = getGatesForCompetitor(comp);
    const idx = gates.findIndex((g) => g.gate === comp.current_ph);
    if (idx >= 0 && idx < sections.length) sections[idx]++;
  }

  return {
    waiting,
    departed: departed.length,
    inCourse: Math.max(0, inCourse),
    sections,
    arrived: arrived.length,
    dns: dnsCount,
    abandons: abandonCount,
  };
});
</script>

<template>
  <div class="summary">
    <div class="summary-item"><strong>En attente</strong> {{ counters.waiting }}</div>
    <div class="summary-item"><strong>Partis</strong> {{ counters.departed }}</div>
    <div class="summary-item"><strong>En course</strong> {{ counters.inCourse }}</div>
    <div class="summary-item" v-for="(count, idx) in counters.sections" :key="idx">
      <strong>Section {{ idx + 1 }}</strong> {{ count }}
    </div>
    <div class="summary-item"><strong>Arrivés</strong> {{ counters.arrived }}</div>
    <div class="summary-item"><strong>DNS</strong> {{ counters.dns }}</div>
    <div class="summary-item"><strong>Abandons</strong> {{ counters.abandons }}</div>
  </div>
</template>

<style scoped>
.summary {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.5rem;
}

.summary-item {
  font-size: 0.85rem;
}

.summary-item strong {
  margin-right: 0.25rem;
}
</style>
