<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import EventHeader from "../../components/EventHeader.vue";
import PhTable from "../../components/suivi/PhTable.vue";
import BeaconEditTable from "../../components/suivi/BeaconEditTable.vue";
import CompetitorActions from "../../components/suivi/CompetitorActions.vue";
import CompetitorHistory from "../../components/suivi/CompetitorHistory.vue";
import SummaryCounters from "../../components/suivi/SummaryCounters.vue";
import { useClock } from "../../composables/useClock";
import { useTimeGates } from "../../composables/useTimeGates";
import { useBeaconEdit } from "../../composables/useBeaconEdit";
import { useCompetitorActions } from "../../composables/useCompetitorActions";
import { useInlineEdit } from "../../composables/useInlineEdit";
import { useDepartureActions } from "../../composables/useDepartureActions";
import { useGpsStatus } from "../../composables/useGpsStatus";
import { formatTime } from "../../utils/date";
import { copyPhone } from "../../utils/clipboard";
import { useEventStore } from "../../stores/event-store";
import { useWebSocket } from "../../composables/use-websocket";
import type { TimeGateEntry } from "../../types/event";
import type { TrackingCompetitor } from "../../types/competitor";
import type { PhRow } from "../../components/suivi/PhTable.vue";

const route = useRoute();
const router = useRouter();
const eventId = route.params.id as string;
const { currentTime } = useClock();

const store = useEventStore();
const { name: eventName, competitors, timeGates, loading } = storeToRefs(store);

const expandedId = ref<string | null>(null);

const { connected, reconnect } = useWebSocket(eventId);

const tg = useTimeGates(timeGates, currentTime, competitors);
const be = useBeaconEdit(eventId, competitors);
const actions = useCompetitorActions(eventId, competitors);
const { editValue, startEdit, cancelEdit, isEditing, clearEdit } = useInlineEdit();
const da = useDepartureActions(eventId, competitors);
const { gpsStatuses } = useGpsStatus(eventId);

async function loadData() {
  const ok = await store.fetchTracking(eventId);
  if (!ok) {
    router.push("/login");
    return;
  }
  for (const comp of competitors.value) {
    be.initInputs(comp);
  }
}

watch(competitors, (newComps) => {
  for (const comp of newComps) {
    be.syncInputs(comp);
  }
});

const sortedCompetitors = computed(() => {
  return [...competitors.value].sort((a, b) => {
    const timeA = a.start_time_planned || "99:99";
    const timeB = b.start_time_planned || "99:99";
    if (timeA !== timeB) return timeA.localeCompare(timeB);
    return (a.start_order || 99) - (b.start_order || 99);
  });
});

function computePhRows(comp: TrackingCompetitor): PhRow[] {
  return tg.getGatesForCompetitor(comp).map((gate: TimeGateEntry, idx: number) => {
    const elapsed = tg.getElapsedMinutes(comp, idx);
    return {
      gate: gate.gate,
      min: comp.sex === "F" ? gate.min_f : gate.min_m,
      max: comp.sex === "F" ? gate.max_f : gate.max_m,
      elapsed,
      status: tg.getStatus(comp, idx),
      colorClass: tg.getElapsedColor(comp, idx, elapsed),
    };
  });
}

function toggleExpand(userId: string) {
  expandedId.value = expandedId.value === userId ? null : userId;
}

async function handleSaveEdit(userId: string, field: string) {
  await da.saveRegistrationField(userId, field, editValue.value || null);
  clearEdit();
}

async function handleConfirmDepartureWithTime(userId: string) {
  if (!editValue.value) { cancelEdit(); return; }
  await da.confirmDepartureWithTime(userId, editValue.value);
  clearEdit();
}

onMounted(loadData);
</script>

<template>
  <div class="suivi-view">
    <EventHeader :event-id="eventId" :event-name="eventName" />
    <div v-if="!connected" class="offline-banner">
      ⚠️ Hors ligne — données potentiellement obsolètes
      <button class="reconnect-btn" @click="reconnect">Se reconnecter</button>
    </div>
    <div class="clock">{{ formatTime(currentTime) }}</div>
    <div v-if="loading" class="loading">Chargement…</div>

    <template v-else>
      <div class="competitor-list">
        <div
          v-for="comp in sortedCompetitors"
          :key="comp.user_id"
          :class="['competitor-card', tg.getRowClass(comp)]"
        >
          <!-- Summary line -->
          <div class="comp-line" @click="toggleExpand(comp.user_id)">
            <span :class="['comp-name', { strikethrough: comp.dns }]">
              {{ comp.last_name }} {{ comp.first_name }}
            </span>
            <span class="comp-ph">
              {{ comp.current_ph === "Arrivé" && comp.sex === "F" ? "Arrivée" : comp.current_ph || "—" }}
            </span>
            <span v-if="tg.getElapsedSinceLastPh(comp)" class="comp-elapsed">
              {{ tg.getElapsedSinceLastPh(comp) }}
            </span>
            <span v-if="gpsStatuses[comp.user_id]" :class="['gps-dot', `gps-${gpsStatuses[comp.user_id]}`]"></span>
            <span v-if="comp.tracker_number && !comp.tracker_returned" class="comp-tracker">📡</span>
            <button v-if="!comp.departed && !comp.dns" class="depart-btn" @click.stop="da.confirmDeparture(comp.user_id)">DÉPART</button>
            <span v-else-if="comp.departed" class="departed-label">Parti à {{ comp.departure_time?.substring(0, 5) || "—" }}</span>
            <button class="expand-btn">{{ expandedId === comp.user_id ? "−" : "+" }}</button>
          </div>

          <!-- Expanded panel -->
          <div v-if="expandedId === comp.user_id" class="expand-panel">
            <div class="section-depart">
              <div v-if="comp.phone" class="field-row">
                <span class="field-label">Téléphone :</span>
                <span class="phone-value" @click="copyPhone(comp.phone)">{{ comp.phone }}</span>
                <a :href="`tel:${comp.phone}`" class="phone-call">📞</a>
              </div>

              <div class="field-row">
                <span class="field-label">Horaire prévu :</span>
                <template v-if="!isEditing(comp.user_id, 'start_time_planned')">
                  <span class="field-value">{{ comp.start_time_planned || "—" }}</span>
                  <button class="edit-btn" @click="startEdit(comp.user_id, 'start_time_planned', comp.start_time_planned)">✏️</button>
                </template>
                <template v-else>
                  <input v-model="editValue" type="time" class="edit-input" />
                  <button class="confirm-btn" @click="handleSaveEdit(comp.user_id, 'start_time_planned')">✓</button>
                  <button class="cancel-btn" @click="cancelEdit()">✗</button>
                </template>
              </div>

              <div class="field-row">
                <span class="field-label">Départ réel :</span>
                <template v-if="!isEditing(comp.user_id, 'actual_departure')">
                  <span class="field-value">{{ comp.departure_time ? comp.departure_time.substring(0, 5) : "—" }}</span>
                  <button class="edit-btn" @click="startEdit(comp.user_id, 'actual_departure', comp.departure_time ? comp.departure_time.substring(0, 5) : comp.start_time_planned)">✏️</button>
                </template>
                <template v-else>
                  <input v-model="editValue" type="time" class="edit-input" />
                  <button class="confirm-btn" @click="handleConfirmDepartureWithTime(comp.user_id)">✓</button>
                  <button class="cancel-btn" @click="cancelEdit()">✗</button>
                </template>
              </div>

              <div class="field-row">
                <span class="field-label">Parcours :</span>
                <template v-if="!isEditing(comp.user_id, 'course_number')">
                  <span class="field-value">{{ comp.course_number || "—" }}</span>
                  <button class="edit-btn" @click="startEdit(comp.user_id, 'course_number', comp.course_number)">✏️</button>
                </template>
                <template v-else>
                  <input v-model="editValue" type="number" min="1" max="6" class="edit-input edit-input-sm" />
                  <button class="confirm-btn" @click="handleSaveEdit(comp.user_id, 'course_number')">✓</button>
                  <button class="cancel-btn" @click="cancelEdit()">✗</button>
                </template>
              </div>

              <div class="field-row">
                <span class="field-label">N° tracker :</span>
                <template v-if="!isEditing(comp.user_id, 'tracker_number')">
                  <span class="field-value">{{ comp.tracker_number || "—" }}</span>
                  <button class="edit-btn" @click="startEdit(comp.user_id, 'tracker_number', comp.tracker_number)">✏️</button>
                </template>
                <template v-else>
                  <input v-model="editValue" type="text" class="edit-input edit-input-sm" />
                  <button class="confirm-btn" @click="handleSaveEdit(comp.user_id, 'tracker_number')">✓</button>
                  <button class="cancel-btn" @click="cancelEdit()">✗</button>
                </template>
              </div>

              <div class="field-row">
                <span class="field-label">Poids sac (kg) :</span>
                <template v-if="!isEditing(comp.user_id, 'bag_weight')">
                  <span class="field-value">{{ comp.bag_weight_start != null ? comp.bag_weight_start : "—" }}</span>
                  <button class="edit-btn" @click="startEdit(comp.user_id, 'bag_weight', comp.bag_weight_start)">✏️</button>
                </template>
                <template v-else>
                  <input v-model="editValue" type="number" step="0.1" min="0" class="edit-input edit-input-sm" />
                  <button class="confirm-btn" @click="handleSaveEdit(comp.user_id, 'bag_weight')">✓</button>
                  <button class="cancel-btn" @click="cancelEdit()">✗</button>
                </template>
              </div>

              <div class="expand-actions">
                <button v-if="!comp.dns && !comp.departed" class="action-btn dns-btn" @click="da.markDns(comp.user_id)">Absent</button>
                <button v-if="comp.dns" class="action-btn cancel-dns-btn" @click="da.cancelDns(comp.user_id)">Annuler absent</button>
                <button v-if="comp.departed" class="action-btn cancel-depart-btn" @click="da.cancelDeparture(comp.user_id)">Annuler le départ</button>
              </div>
            </div>

            <template v-if="comp.departed">
              <PhTable :rows="computePhRows(comp)" />

              <BeaconEditTable
                :beacons="comp.beacons"
                :inputs="be.getInputs(comp.user_id)"
                :saving-b-idx="be.savingRow.value?.userId === comp.user_id ? be.savingRow.value.bIdx : null"
                :ph-arrival-inputs="be.getPhArrivalInputs(comp.user_id)"
                @save="(bIdx: number) => be.saveRow(comp.user_id, bIdx)"
                @cancel="(bIdx: number) => be.resetRow(comp.user_id, bIdx)"
                @fill-time="(bIdx: number) => be.fillCurrentTime(comp.user_id, bIdx)"
                @save-ph-arrival="(bIdx: number) => be.savePhArrival(comp.user_id, bIdx)"
                @cancel-ph-arrival="(bIdx: number) => be.resetPhArrival(comp.user_id, bIdx)"
                @fill-ph-arrival-time="(bIdx: number) => be.fillPhArrivalCurrentTime(comp.user_id, bIdx)"
              />

              <CompetitorActions
                :departed="comp.departed"
                :dns="comp.dns"
                :abandoned="comp.abandoned"
                :tracker-returned="comp.tracker_returned"
                :tracker-number="comp.tracker_number"
                @abandon="actions.markAbandon(comp.user_id)"
                @cancel-abandon="actions.cancelAbandon(comp.user_id)"
                @tracker-returned="actions.markTrackerReturned(comp.user_id)"
                @cancel-tracker-returned="actions.cancelTrackerReturned(comp.user_id)"
              />
            </template>

            <CompetitorHistory :logs="comp.logs" />
          </div>
        </div>
      </div>

      <SummaryCounters :competitors="competitors" :all-time-gates="timeGates" />
    </template>
  </div>
</template>

<style scoped>
.suivi-view { max-width: 700px; margin: 0 auto; padding: 0 0.5rem 1rem; }

.offline-banner {
  background: #fff3e0; border: 1px solid #ff9800; border-radius: 6px;
  padding: 0.5rem 0.75rem; margin: 0.5rem 0; font-size: 0.85rem;
  display: flex; align-items: center; gap: 0.75rem;
}
.reconnect-btn {
  margin-left: auto; padding: 0.3rem 0.75rem; font-size: 0.8rem; font-weight: 600;
  background: #ff9800; color: #fff; border: none; border-radius: 4px; cursor: pointer;
}

.clock {
  position: sticky; top: 80px; background: #fff; z-index: 90;
  text-align: center; font-size: 2rem; font-weight: 700;
  font-variant-numeric: tabular-nums; padding: 0.5rem 0;
  border-bottom: 1px solid #e0e0e0;
}

.loading { text-align: center; padding: 2rem; color: #666; }
.competitor-list { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.75rem; }

.competitor-card {
  border: 1px solid #e0e0e0; border-radius: 8px;
  padding: 0.75rem; transition: background-color 0.2s;
}

.row-default { background-color: #fff; }
.row-next { background-color: #e8f5e9; border-color: #4caf50; }
.row-upcoming { background-color: #fff3e0; border-color: #ff9800; }
.row-waiting { background-color: #fff; }
.row-late { background-color: #ffebee; border-color: #f44336; }
.row-arrived { background-color: #f5f5f5; opacity: 0.7; }
.row-dns, .row-abandon { background-color: #f3e5f5; opacity: 0.8; }

.comp-line { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.comp-name { font-weight: 700; font-size: 1rem; flex: 1; }
.strikethrough { text-decoration: line-through; color: #999; }
.comp-ph { font-size: 0.85rem; font-weight: 600; color: #1976d2; }
.comp-elapsed { font-size: 0.85rem; font-weight: 600; font-variant-numeric: tabular-nums; color: #555; }
.comp-tracker { font-size: 1rem; }
.gps-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; vertical-align: middle; }
.gps-green { background-color: #4caf50; }
.gps-orange { background-color: #ff9800; }
.gps-red { background-color: #f44336; }

.expand-btn {
  width: 28px; height: 28px; border: 1px solid #ccc; border-radius: 50%;
  background: #fff; cursor: pointer; font-size: 1rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.expand-panel {
  margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e0e0e0;
  display: flex; flex-direction: column; gap: 0.75rem;
}

.section-info { display: flex; flex-direction: column; gap: 0.25rem; }
.field-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
.field-label { font-weight: 600; min-width: 130px; }
.field-value { color: #333; }
.phone-value { color: #1976d2; cursor: pointer; text-decoration: underline; }
.phone-call { text-decoration: none; font-size: 1.1rem; }

.depart-btn {
  padding: 0.3rem 1rem; font-size: 0.8rem; font-weight: 700;
  color: #fff; background-color: #1976d2; border: none;
  border-radius: 6px; cursor: pointer; white-space: nowrap;
}
.depart-btn:hover { background-color: #1565c0; }
.depart-btn:active { background-color: #0d47a1; }
.departed-label { font-size: 0.8rem; color: #666; font-style: italic; white-space: nowrap; }

.section-depart {
  display: flex; flex-direction: column; gap: 0.5rem;
  padding-bottom: 0.75rem; border-bottom: 1px solid #e0e0e0;
}

.edit-btn { background: none; border: none; cursor: pointer; font-size: 0.85rem; padding: 0.1rem 0.3rem; }
.edit-input { padding: 0.25rem 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.85rem; width: 100px; }
.edit-input-sm { width: 60px; }
.confirm-btn, .cancel-btn { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0.1rem 0.4rem; }
.confirm-btn { color: #4caf50; }
.cancel-btn { color: #f44336; }

.expand-actions {
  display: flex; gap: 0.5rem; margin-top: 0.25rem;
  padding-top: 0.5rem; border-top: 1px solid #eee;
}
.action-btn {
  padding: 0.4rem 0.75rem; font-size: 0.8rem; font-weight: 600;
  border: 1px solid; border-radius: 4px; cursor: pointer; background: #fff;
}
.dns-btn { color: #f44336; border-color: #f44336; }
.dns-btn:hover { background: #ffebee; }
.cancel-dns-btn { color: #ff9800; border-color: #ff9800; }
.cancel-dns-btn:hover { background: #fff3e0; }
.cancel-depart-btn { color: #ff9800; border-color: #ff9800; }
.cancel-depart-btn:hover { background: #fff3e0; }
</style>
