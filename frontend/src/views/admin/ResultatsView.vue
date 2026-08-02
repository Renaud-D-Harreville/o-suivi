<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import EventHeader from "../../components/EventHeader.vue";
import { useEventStore } from "../../stores/event-store";
import { apiFetch } from "../../utils/api";
import type { CompetitorResult, ResultsData } from "../../types/results";
import { formatDuration, formatResultTime, formatDelay, globalIcon, sectionIcon, beaconIcon } from "../../utils/format";

const route = useRoute();
const router = useRouter();
const eventId = route.params.id as string;

const store = useEventStore();
const { name: eventName } = storeToRefs(store);

// --- State ---

const resultsData = ref<ResultsData | null>(null);
const loading = ref(true);
const expandedId = ref<string | null>(null);

// --- Data fetching ---

async function fetchData() {
  try {
    const [nameOk, resultsRes] = await Promise.all([
      store.fetchEventName(eventId),
      apiFetch(`/api/events/${eventId}/resultats`),
    ]);

    if (!nameOk || resultsRes.status === 401) {
      router.push("/login");
      return;
    }


    if (resultsRes.ok) {
      resultsData.value = await resultsRes.json();
    }
  } catch (err) {
    console.error("Failed to fetch results:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

// --- Helpers ---

function toggleExpand(userId: string) {
  expandedId.value = expandedId.value === userId ? null : userId;
}

function competitorGlobalIcon(c: CompetitorResult): string {
  return globalIcon(c.dns, c.valid_global);
}
</script>

<template>
  <div class="resultats-view">
    <EventHeader :event-id="eventId" :event-name="eventName" />

    <main class="content">
      <div v-if="loading" class="loading">Chargement des résultats…</div>

      <template v-else-if="resultsData">
        <!-- Routechoices link -->
        <div v-if="resultsData.routechoices_url" class="routechoices-link">
          <a :href="resultsData.routechoices_url" target="_blank" rel="noopener">
            🗺️ Voir les traces GPS sur Routechoices
          </a>
        </div>

        <!-- Empty state -->
        <div v-if="resultsData.competitors.length === 0" class="empty">
          Aucun résultat disponible.
        </div>

        <!-- Competitor list -->
        <div class="competitor-list">
          <div
            v-for="comp in resultsData.competitors"
            :key="comp.user_id"
            :class="['competitor-card', { dns: comp.dns, expanded: expandedId === comp.user_id }]"
            @click="!comp.dns && toggleExpand(comp.user_id)"
          >
            <!-- Line 1: Name + global result -->
            <div class="card-line1">
              <span class="name">{{ comp.first_name }} {{ comp.last_name }}</span>
              <span v-if="comp.abandoned" class="badge abandoned">ABANDON</span>
              <span v-if="comp.dns" class="badge dns-badge">DNS</span>
              <span class="global-result">{{ competitorGlobalIcon(comp) }}</span>
            </div>

            <!-- Line 2: PH statuses -->
            <div class="card-line2">
              <span v-for="section in comp.sections" :key="section.gate" class="ph-status">
                {{ section.gate }} {{ sectionIcon(section.valid) }}
              </span>
            </div>

            <!-- Expanded detail panel -->
            <div v-if="expandedId === comp.user_id && !comp.dns" class="detail-panel" @click.stop>
              <!-- General info -->
              <section class="detail-section">
                <h3>Informations générales</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">Poids du sac</span>
                    <span class="value">
                      {{ comp.bag_weight_start != null ? `${comp.bag_weight_start} kg` : '-' }}
                      →
                      {{ comp.bag_weight_end != null ? `${comp.bag_weight_end} kg` : '-' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="label">Heure de départ</span>
                    <span class="value">{{ formatResultTime(comp.departure_time) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Heure d'arrivée</span>
                    <span class="value">{{ formatResultTime(comp.arrival_time) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Temps total</span>
                    <span class="value">{{ formatDuration(comp.total_time) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Temps en course (hors pauses)</span>
                    <span class="value">{{ formatDuration(comp.total_running_time) }}</span>
                  </div>
                </div>
              </section>

              <!-- Section summary -->
              <section class="detail-section">
                <h3>Résumé par section</h3>
                <table class="section-table">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Statut</th>
                      <th>Retard</th>
                      <th>Temps section</th>
                      <th>Temps course</th>
                      <th>Pause</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="section in comp.sections" :key="section.gate">
                      <td>{{ section.gate }}</td>
                      <td>{{ sectionIcon(section.valid) }}</td>
                      <td :class="{ 'delay-early': section.delay !== null && section.delay < 0, 'delay-late': section.delay !== null && section.delay > 0 }">
                        {{ formatDelay(section.delay) }}
                      </td>
                      <td>{{ formatDuration(section.section_time) }}</td>
                      <td>{{ formatDuration(section.running_time) }}</td>
                      <td>{{ formatDuration(section.pause_time) }}</td>
                    </tr>
                  </tbody>
                </table>
              </section>

              <!-- Beacon detail -->
              <section class="detail-section">
                <h3>Liste détaillée des balises</h3>
                <table class="beacon-table">
                  <thead>
                    <tr>
                      <th>N°</th>
                      <th>Code saisi</th>
                      <th>Validité</th>
                      <th>Temps inter.</th>
                      <th>Cumulé section</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="beacon in comp.beacons" :key="beacon.sequence">
                      <td>{{ beacon.beacon_number }}<span v-if="beacon.tag !== 'unique'" class="tag">{{ beacon.tag }}</span></td>
                      <td>{{ beacon.entered_code || '-' }}</td>
                      <td>{{ beaconIcon(beacon.valid) }}</td>
                      <td>{{ formatDuration(beacon.split_time) }}</td>
                      <td>{{ formatDuration(beacon.cumulated_section_time) }}</td>
                    </tr>
                  </tbody>
                </table>
              </section>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.resultats-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.content {
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.routechoices-link {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: #e3f2fd;
  border-radius: 8px;
}

.routechoices-link a {
  color: #1565c0;
  text-decoration: none;
  font-weight: 500;
}

.routechoices-link a:hover {
  text-decoration: underline;
}

/* --- Competitor cards --- */

.competitor-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.competitor-card {
  background: #fff;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  transition: box-shadow 0.15s;
}

.competitor-card:hover:not(.dns) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.competitor-card.expanded {
  border-color: #1976d2;
}

.competitor-card.dns {
  background: #f5f5f5;
  opacity: 0.7;
  cursor: default;
}

.competitor-card.dns .name {
  text-decoration: line-through;
  color: #999;
}

.card-line1 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.name {
  font-weight: 600;
  font-size: 0.95rem;
  flex: 1;
}

.global-result {
  font-size: 1.1rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge.abandoned {
  background: #fff3e0;
  color: #e65100;
}

.badge.dns-badge {
  background: #eceff1;
  color: #546e7a;
}

.card-line2 {
  margin-top: 0.25rem;
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #555;
}

.ph-status {
  white-space: nowrap;
}

/* --- Detail panel --- */

.detail-panel {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eee;
  cursor: default;
}

.detail-section {
  margin-bottom: 1rem;
}

.detail-section h3 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.info-item .label {
  font-size: 0.75rem;
  color: #888;
}

.info-item .value {
  font-size: 0.9rem;
  font-weight: 500;
}

/* --- Tables --- */

.section-table,
.beacon-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.section-table th,
.beacon-table th {
  text-align: left;
  font-weight: 600;
  padding: 0.4rem 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  color: #555;
  white-space: nowrap;
}

.section-table td,
.beacon-table td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.delay-early {
  color: #1565c0;
  font-weight: 500;
}

.delay-late {
  color: #c62828;
  font-weight: 500;
}

.tag {
  font-size: 0.7rem;
  color: #888;
  margin-left: 0.25rem;
}
</style>

