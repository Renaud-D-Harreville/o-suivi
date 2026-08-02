<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import EventHeader from "../../components/EventHeader.vue";
import { useClock } from "../../composables/useClock";
import { useInlineEdit } from "../../composables/useInlineEdit";
import { useDepartureActions } from "../../composables/useDepartureActions";
import { formatTime } from "../../utils/date";
import { copyPhone } from "../../utils/clipboard";
import { useEventStore } from "../../stores/event-store";
import { useWebSocket } from "../../composables/use-websocket";
import type { TrackingCompetitor } from "../../types/competitor";

const route = useRoute();
const router = useRouter();
const eventId = route.params.id as string;
const { currentTime } = useClock();

const store = useEventStore();
const { name: eventName, competitors, loading } = storeToRefs(store);

const expandedId = ref<string | null>(null);

const { connected, reconnect } = useWebSocket(eventId);

const { editValue, startEdit, cancelEdit, isEditing, clearEdit } = useInlineEdit();
const da = useDepartureActions(eventId, competitors);

async function loadData() {
  const ok = await store.fetchTracking(eventId);
  if (!ok) router.push("/login");
}

const sortedCompetitors = computed(() => {
  return [...competitors.value].sort((a, b) => {
    const timeA = a.start_time_planned || "99:99";
    const timeB = b.start_time_planned || "99:99";
    if (timeA !== timeB) return timeA.localeCompare(timeB);
    return (a.course_number || 99) - (b.course_number || 99);
  });
});

function getRowColor(competitor: TrackingCompetitor): string {
  if (competitor.departed || competitor.dns) return "departed";

  const pendingTimes = competitors.value
    .filter((c) => !c.departed && !c.dns)
    .map((c) => c.start_time_planned || "99:99")
    .sort();

  if (pendingTimes.length === 0) return "waiting";

  const firstTime = pendingTimes[0];
  const uniqueTimes = [...new Set(pendingTimes)];
  const secondTime = uniqueTimes.length > 1 ? uniqueTimes[1] : null;
  const competitorTime = competitor.start_time_planned || "99:99";

  if (competitorTime === firstTime) return "next";
  if (secondTime && competitorTime === secondTime) return "upcoming";
  return "waiting";
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

function toggleExpand(userId: string) {
  expandedId.value = expandedId.value === userId ? null : userId;
}

onMounted(loadData);
</script>

<template>
  <div class="depart-view">
    <EventHeader :event-id="eventId" :event-name="eventName" />
    <div v-if="!connected" class="offline-banner">
      ⚠️ Hors ligne — données potentiellement obsolètes
      <button class="reconnect-btn" @click="reconnect">Se reconnecter</button>
    </div>
    <div class="clock">{{ formatTime(currentTime) }}</div>
    <div v-if="loading" class="loading">Chargement…</div>

    <div v-else class="competitor-list">
      <div
        v-for="comp in sortedCompetitors"
        :key="comp.user_id"
        :class="['competitor-card', getRowColor(comp), { dns: comp.dns }]"
      >
        <div class="comp-name">
          <span :class="{ strikethrough: comp.dns }">{{ comp.last_name }} {{ comp.first_name }}</span>
        </div>

        <div class="comp-info">
          <span class="info-item">{{ comp.start_time_planned || "—" }}</span>
          <span class="info-item">Parcours {{ comp.course_number || "—" }}</span>
          <span v-if="comp.tracker_number" class="info-item">Tracker #{{ comp.tracker_number }}</span>
          <button class="expand-btn" @click="toggleExpand(comp.user_id)">
            {{ expandedId === comp.user_id ? "−" : "+" }}
          </button>
        </div>

        <div v-if="!comp.departed && !comp.dns" class="comp-action">
          <button class="depart-btn" @click="da.confirmDeparture(comp.user_id)">DÉPART</button>
        </div>
        <div v-else-if="comp.departed" class="comp-action">
          <span class="departed-label">Parti à {{ comp.departure_time?.substring(11, 16) || "—" }}</span>
        </div>

        <!-- Expandable panel -->
        <div v-if="expandedId === comp.user_id" class="expand-panel">
          <div class="field-row" v-if="comp.phone">
            <span class="field-label">Téléphone :</span>
            <span class="phone-value" @click="copyPhone(comp.phone)">{{ comp.phone }}</span>
            <a :href="`tel:${comp.phone}`" class="phone-call">📞</a>
          </div>

          <!-- Editable: Start time planned -->
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

          <!-- Editable: Actual departure time -->
          <div class="field-row">
            <span class="field-label">Départ réel :</span>
            <template v-if="!isEditing(comp.user_id, 'actual_departure')">
              <span class="field-value">{{ comp.departure_time ? comp.departure_time.substring(11, 16) : "—" }}</span>
              <button class="edit-btn" @click="startEdit(comp.user_id, 'actual_departure', comp.departure_time ? comp.departure_time.substring(11, 16) : comp.start_time_planned)">✏️</button>
            </template>
            <template v-else>
              <input v-model="editValue" type="time" class="edit-input" />
              <button class="confirm-btn" @click="handleConfirmDepartureWithTime(comp.user_id)">✓</button>
              <button class="cancel-btn" @click="cancelEdit()">✗</button>
            </template>
          </div>

          <!-- Editable: Course number -->
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

          <!-- Editable: Tracker -->
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

          <!-- Editable: Bag weight -->
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
      </div>
    </div>
  </div>
</template>

<style scoped>
.depart-view { max-width: 600px; margin: 0 auto; padding: 0 0.5rem 1rem; }

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

.competitor-card.departed { background-color: #f5f5f5; opacity: 0.7; }
.competitor-card.next { background-color: #e8f5e9; border-color: #4caf50; }
.competitor-card.upcoming { background-color: #fff3e0; border-color: #ff9800; }
.competitor-card.waiting { background-color: #fff; }
.competitor-card.dns { background-color: #f5f5f5; opacity: 0.7; }

.comp-name { font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem; }
.strikethrough { text-decoration: line-through; color: #999; }

.comp-info { display: flex; align-items: center; gap: 0.75rem; font-size: 0.85rem; color: #555; }
.info-item { white-space: nowrap; }

.expand-btn {
  margin-left: auto; width: 28px; height: 28px; border: 1px solid #ccc;
  border-radius: 50%; background: #fff; cursor: pointer; font-size: 1rem;
  font-weight: 700; display: flex; align-items: center; justify-content: center;
}

.comp-action { text-align: center; margin-top: 0.5rem; }

.depart-btn {
  padding: 0.5rem 2rem; font-size: 1rem; font-weight: 700;
  color: #fff; background-color: #1976d2; border: none;
  border-radius: 6px; cursor: pointer;
}
.depart-btn:hover { background-color: #1565c0; }
.depart-btn:active { background-color: #0d47a1; }

.departed-label { font-size: 0.85rem; color: #666; font-style: italic; }

.expand-panel {
  margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e0e0e0;
  display: flex; flex-direction: column; gap: 0.5rem;
}

.field-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
.field-label { font-weight: 600; min-width: 130px; }
.field-value { color: #333; }
.phone-value { color: #1976d2; cursor: pointer; text-decoration: underline; }
.phone-call { text-decoration: none; font-size: 1.1rem; }

.edit-btn { background: none; border: none; cursor: pointer; font-size: 0.85rem; padding: 0.1rem 0.3rem; }
.edit-input { padding: 0.25rem 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.85rem; width: 100px; }
.edit-input-sm { width: 60px; }

.confirm-btn, .cancel-btn { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0.1rem 0.4rem; }
.confirm-btn { color: #4caf50; }
.cancel-btn { color: #f44336; }

.expand-actions {
  display: flex; gap: 0.5rem; margin-top: 0.5rem;
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

