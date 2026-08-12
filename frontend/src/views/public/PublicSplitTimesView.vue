<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import type { SplitsResponse, CompetitorSummary, EventBeaconInfo } from "../../types/splits";
import { formatDuration, shortName } from "../../utils/format";
import AdminBackLink from "../../components/AdminBackLink.vue";

const route = useRoute();
const eventId = route.params.id as string;

const data = ref<SplitsResponse | null>(null);
const loading = ref(true);

async function fetchData() {
  try {
    const res = await fetch(`/api/public/events/${eventId}/splits`);
    if (res.ok) {
      data.value = await res.json();
    }
  } catch (err) {
    console.error("Failed to fetch split times:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

// --- Lookup maps ---

const beaconMap = computed(() => {
  if (!data.value) return new Map<number, EventBeaconInfo>();
  return new Map(data.value.beacons.map((b) => [b.id, b]));
});

const competitorMap = computed(() => {
  if (!data.value) return new Map<string, CompetitorSummary>();
  return new Map(data.value.competitors.map((c) => [c.user_id, c]));
});

// --- Helpers ---

function beaconLabel(beaconId: number | null): string {
  if (beaconId === null) return "Départ";
  const b = beaconMap.value.get(beaconId);
  if (!b) return `?`;
  return b.tag === "unique" ? `Balise ${b.number}` : `Balise ${b.number}-${b.tag}`;
}

function pairTitle(fromId: number | null, toId: number): string {
  return `${beaconLabel(fromId)} → ${beaconLabel(toId)}`;
}

function competitorName(userId: string): string {
  const c = competitorMap.value.get(userId);
  if (!c) return "?";
  return shortName(c.first_name, c.last_name);
}

function competitorCourse(userId: string): string {
  const c = competitorMap.value.get(userId);
  if (!c || c.course_number === null) return "-";
  return `P${c.course_number}`;
}

function computeRank(index: number, splits: { split_seconds: number }[]): number {
  if (index === 0) return 1;
  if (splits[index].split_seconds === splits[index - 1].split_seconds) {
    return computeRank(index - 1, splits);
  }
  return index + 1;
}
</script>

<template>
  <div class="split-times-view">
    <header class="public-header">
      <AdminBackLink :to="`/admin/events/${eventId}/suivi`" />
      <router-link :to="`/events/${eventId}`" class="back-link">← Retour aux résultats</router-link>
      <h1>Comparaison des temps intermédiaires</h1>
      <p v-if="data" class="event-name">{{ data.event_name }}</p>
    </header>

    <main class="content">
      <div v-if="loading" class="loading">Chargement…</div>

      <template v-else-if="data">
        <div v-if="data.pairs.length === 0" class="empty">
          Aucun temps intermédiaire disponible.
        </div>

        <div v-for="pair in data.pairs" :key="`${pair.from_beacon_id}-${pair.to_beacon_id}`" class="pair-block">
          <h2 class="pair-title">{{ pairTitle(pair.from_beacon_id, pair.to_beacon_id) }}</h2>

          <div v-if="pair.splits.length === 0" class="pair-empty">Aucun temps enregistré.</div>

          <table v-else class="split-table">
            <thead>
              <tr>
                <th class="col-rank">#</th>
                <th class="col-name">Concurrent</th>
                <th class="col-course">Parcours</th>
                <th class="col-split">Split</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, idx) in pair.splits" :key="entry.user_id">
                <td class="col-rank">{{ computeRank(idx, pair.splits) }}</td>
                <td class="col-name">{{ competitorName(entry.user_id) }}</td>
                <td class="col-course">{{ competitorCourse(entry.user_id) }}</td>
                <td class="col-split">{{ formatDuration(entry.split_seconds) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.split-times-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.public-header {
  background: #1976d2;
  color: #fff;
  padding: 1rem;
  text-align: center;
  position: relative;
}

.public-header h1 {
  margin: 0.25rem 0;
  font-size: 1.2rem;
}

.event-name {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.85;
}

.back-link {
  color: #bbdefb;
  text-decoration: none;
  font-size: 0.85rem;
  display: inline-block;
  margin-bottom: 0.25rem;
}

.back-link:hover {
  color: #fff;
}

.content {
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.pair-block {
  margin-bottom: 1.5rem;
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e0e0e0;
}

.pair-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}

.pair-empty {
  color: #999;
  font-style: italic;
  font-size: 0.85rem;
}

.split-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.split-table th {
  text-align: left;
  font-weight: 600;
  padding: 0.4rem 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  color: #555;
  white-space: nowrap;
}

.split-table td {
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.col-rank {
  width: 2.5rem;
  text-align: center;
  font-weight: 600;
  color: #888;
}

.col-course {
  width: 4rem;
  text-align: center;
  color: #666;
}

.col-split {
  width: 5rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}

.split-table tbody tr:first-child .col-rank {
  color: #f9a825;
  font-weight: 700;
}
</style>

