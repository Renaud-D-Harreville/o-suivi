<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { shortName } from "../../utils/format";
import AdminBackLink from "../../components/AdminBackLink.vue";

interface ScheduleEntry {
  first_name: string;
  last_name_initial: string;
  phone: string | null;
  start_time_planned: string | null;
}

interface ScheduleData {
  event_name: string;
  entries: ScheduleEntry[];
}

const route = useRoute();
const eventId = route.params.id as string;

const data = ref<ScheduleData | null>(null);
const loading = ref(true);

async function fetchData() {
  try {
    const res = await fetch(`/api/public/events/${eventId}/schedule`);
    if (res.ok) {
      data.value = await res.json();
    }
  } catch (err) {
    console.error("Failed to fetch schedule:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

function displayName(entry: ScheduleEntry): string {
  return shortName(entry.first_name, entry.last_name_initial.replace(".", ""));
}
</script>

<template>
  <div class="schedule-view">
    <header class="public-header">
      <AdminBackLink :to="`/admin/events/${eventId}/config`" />
      <router-link :to="`/events/${eventId}`" class="back-link">← Résultats</router-link>
      <h1>Horaires</h1>
      <p v-if="data" class="event-name">{{ data.event_name }}</p>
    </header>

    <main class="content">
      <div v-if="loading" class="loading">Chargement…</div>

      <template v-else-if="data">
        <div v-if="data.entries.length === 0" class="empty">
          Aucun participant inscrit
        </div>

        <table v-else class="schedule-table">
          <thead>
            <tr>
              <th class="col-time">Horaire</th>
              <th class="col-name">Nom</th>
              <th class="col-phone">Téléphone</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(entry, idx) in data.entries" :key="idx">
              <td class="col-time">{{ entry.start_time_planned ?? "-" }}</td>
              <td class="col-name">{{ displayName(entry) }}</td>
              <td class="col-phone">{{ entry.phone ?? "-" }}</td>
            </tr>
          </tbody>
        </table>
      </template>
    </main>
  </div>
</template>

<style scoped>
.schedule-view {
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
  max-width: 600px;
  margin: 0 auto;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.schedule-table th {
  text-align: left;
  font-weight: 600;
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid #e0e0e0;
  color: #555;
  white-space: nowrap;
}

.schedule-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f0f0f0;
}

.col-time {
  width: 5rem;
  color: #888;
  font-variant-numeric: tabular-nums;
}

.col-phone {
  white-space: nowrap;
  color: #555;
}
</style>

