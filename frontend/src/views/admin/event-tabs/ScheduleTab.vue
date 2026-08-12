<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import draggable from "vuedraggable";
import { useAuth } from "../../../composables/useAuth";

interface Registration {
  user_id: string;
  first_name: string;
  last_name: string;
  sex: string;
  course_number: number | null;
  start_order: number | null;
  start_time_planned: string | null;
  tracker_number: string | null;
  routechoices_short_name: string | null;
}

const props = defineProps<{ eventId: string }>();

const { getAuthHeaders } = useAuth();
const participants = ref<Registration[]>([]);
const groupSize = ref(1);
const intervalSeconds = ref(120);
const firstStartTime = ref("07:30");
const courseCount = ref(4);
const saving = ref(false);
const error = ref("");
const success = ref("");


async function fetchData() {
  try {
    // Fetch event for start_mode, first_start_time, courses count
    const eventRes = await fetch(`/api/events/${props.eventId}`, {
      headers: getAuthHeaders(),
    });
    if (!eventRes.ok) {
      error.value = "Impossible de charger l'événement";
      return;
    }
    const eventData = await eventRes.json();
    firstStartTime.value = eventData.first_start_time ?? "07:30";
    courseCount.value = Math.max(eventData.courses?.length ?? 1, 1);
    if (eventData.start_mode) {
      groupSize.value = eventData.start_mode.group_size ?? 1;
      intervalSeconds.value = eventData.start_mode.interval_seconds ?? 120;
    }

    // Fetch registrations
    const regRes = await fetch(`/api/events/${props.eventId}/registrations`, {
      headers: getAuthHeaders(),
    });
    if (regRes.ok) {
      const regs: Registration[] = await regRes.json();
      // Sort by existing start_order, or default sort (F first, then alpha)
      if (regs.some((r) => r.start_order != null)) {
        regs.sort((a, b) => (a.start_order ?? 999) - (b.start_order ?? 999));
      } else {
        regs.sort((a, b) => {
          if (a.sex !== b.sex) return a.sex === "F" ? -1 : 1;
          return a.last_name.localeCompare(b.last_name);
        });
      }
      participants.value = regs;
    }
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

function applyPreset(g: number, s: number) {
  groupSize.value = g;
  intervalSeconds.value = s;
}

/** Computed scheduled data with order, course, time. */
const schedule = computed(() => {
  const [hh, mm] = firstStartTime.value.split(":").map(Number);
  const baseMinutes = (hh || 0) * 60 + (mm || 0);
  const intervalMin = intervalSeconds.value / 60;

  return participants.value.map((p, index) => {
    const order = index + 1;
    const course = ((index % courseCount.value) + 1);
    const slotIndex = Math.floor(index / groupSize.value);
    const totalMin = baseMinutes + slotIndex * intervalMin;
    const h = Math.floor(totalMin / 60);
    const m = Math.round(totalMin % 60);
    const time = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;

    return { ...p, order, course_number: course, start_time_planned: time };
  });
});


async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  const registrations = schedule.value.map((s) => ({
    user_id: s.user_id,
    course_number: s.course_number,
    start_order: s.order,
    start_time_planned: s.start_time_planned,
    tracker_number: s.tracker_number,
    routechoices_short_name: s.routechoices_short_name,
  }));

  const payload = {
    start_mode: {
      group_size: groupSize.value,
      interval_seconds: intervalSeconds.value,
    },
    registrations,
  };

  try {
    const response = await fetch(`/api/events/${props.eventId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      error.value = "Erreur lors de la sauvegarde";
      return;
    }
    success.value = "Enregistré";
    setTimeout(() => (success.value = ""), 2000);
  } catch {
    error.value = "Impossible de contacter le serveur";
  } finally {
    saving.value = false;
  }
}

onMounted(fetchData);
</script>

<template>
  <div class="schedule-tab">
    <div v-if="participants.length === 0" class="empty">
      Aucun participant inscrit. Ajoutez des participants dans l'onglet
      <strong>Participants</strong>.
    </div>

    <div v-else>
      <!-- Start mode config -->
      <div class="start-config">
        <div class="config-fields">
          <div class="field-inline">
            <label>Personnes par départ</label>
            <input v-model.number="groupSize" type="number" min="1" class="input-small" />
          </div>
          <div class="field-inline">
            <label>Intervalle</label>
            <input v-model.number="intervalSeconds" type="number" min="1" class="input-small" />
            <span class="unit">sec</span>
          </div>
        </div>
        <div class="presets">
          <button type="button" class="btn-preset" @click="applyPreset(1, 120)">1 / 2 min</button>
          <button type="button" class="btn-preset" @click="applyPreset(2, 180)">2 / 3 min</button>
        </div>
      </div>

      <!-- Schedule table -->
      <table class="schedule-table">
        <thead>
          <tr>
            <th>↕</th>
            <th>Ordre</th>
            <th>Nom / Prénom</th>
            <th>Sexe</th>
            <th>Parcours</th>
            <th>Horaire</th>
          </tr>
        </thead>
        <draggable
          v-model="participants"
          tag="tbody"
          handle=".drag-handle"
          item-key="user_id"
          :animation="200"
        >
          <template #item="{ element, index }">
            <tr>
              <td class="drag-handle-cell">
                <span class="drag-handle">≡</span>
              </td>
              <td class="order-cell">{{ schedule[index].order }}</td>
              <td>{{ element.last_name }} {{ element.first_name }}</td>
              <td>{{ element.sex }}</td>
              <td class="course-cell">{{ schedule[index].course_number }}</td>
              <td class="time-cell">{{ schedule[index].start_time_planned }}</td>
            </tr>
          </template>
        </draggable>
      </table>

      <p v-if="error" class="msg error">{{ error }}</p>
      <p v-if="success" class="msg success">{{ success }}</p>

      <div class="actions">
        <button type="button" class="btn-save" :disabled="saving" @click="handleSave">
          {{ saving ? "Enregistrement…" : "Enregistrer" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-tab {
  overflow-x: auto;
}

.empty {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-style: italic;
}

.start-config {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.config-fields {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.field-inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-inline label {
  font-size: 0.875rem;
  font-weight: 600;
}

.input-small {
  width: 70px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: right;
}

.unit {
  font-size: 0.8125rem;
  color: #666;
}

.presets {
  display: flex;
  gap: 0.5rem;
}

.btn-preset {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  background: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-preset:hover {
  background: #d0d0d0;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

th {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  font-size: 0.875rem;
  color: #666;
}

td {
  padding: 0.375rem 0.5rem;
  border-bottom: 1px solid #eee;
}

.drag-handle-cell {
  width: 2rem;
  text-align: center;
}

.drag-handle {
  cursor: grab;
  font-size: 1.25rem;
  color: #999;
  user-select: none;
  line-height: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

.sortable-ghost {
  opacity: 0.4;
  background: #e3f2fd;
}

.sortable-drag {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.order-cell {
  font-weight: 600;
  text-align: center;
}

.course-cell {
  text-align: center;
  font-weight: 600;
  color: #1976d2;
}

.time-cell {
  font-family: monospace;
  font-size: 0.9375rem;
}

.msg {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.error {
  color: #d32f2f;
}

.success {
  color: #2e7d32;
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.btn-save {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: #1976d2;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save:hover:not(:disabled) {
  background-color: #1565c0;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

