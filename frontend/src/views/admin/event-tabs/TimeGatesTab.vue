<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuth } from "../../../composables/useAuth";

interface Gate {
  gate: string;
  min_m: number | null;
  max_m: number | null;
  min_f: number | null;
  max_f: number | null;
}

interface CourseTimeGates {
  course_number: number;
  gates: Gate[];
}

interface CourseBeacon {
  id: number;
  number: number;
  tag: string;
  is_ph: boolean;
}

interface Course {
  number: number;
  beacons: CourseBeacon[];
}

const props = defineProps<{ eventId: string }>();

const courses = ref<Course[]>([]);
const timeGates = ref<CourseTimeGates[]>([]);
const referenceTimeGates = ref<CourseTimeGates[]>([]);
const percentages = ref<Record<string, number>>({});
const saving = ref(false);
const error = ref("");
const success = ref("");
const { getAuthHeaders } = useAuth();

function getPhCountForCourse(course: Course): number {
  return course.beacons.filter((b) => b.is_ph).length;
}

function emptyGatesForCourse(course: Course): Gate[] {
  const phCount = getPhCountForCourse(course);
  return Array.from({ length: phCount }, (_, i) => ({
    gate: `PH${i + 1}`,
    min_m: null,
    max_m: null,
    min_f: null,
    max_f: null,
  }));
}

async function fetchEvent() {
  try {
    const response = await fetch(`/api/events/${props.eventId}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      error.value = "Impossible de charger l'événement";
      return;
    }
    const data = await response.json();
    courses.value = data.courses ?? [];
    timeGates.value = data.time_gates ?? [];

    // Ensure each course has time_gates entry with correct PH count
    for (const course of courses.value) {
      const existing = timeGates.value.find((tg) => tg.course_number === course.number);
      if (!existing) {
        timeGates.value.push({ course_number: course.number, gates: emptyGatesForCourse(course) });
      } else {
        // Adjust gate count based on PH beacons
        const phCount = getPhCountForCourse(course);
        while (existing.gates.length < phCount) {
          existing.gates.push({
            gate: `PH${existing.gates.length + 1}`,
            min_m: null,
            max_m: null,
            min_f: null,
            max_f: null,
          });
        }
        if (existing.gates.length > phCount) {
          existing.gates = existing.gates.slice(0, phCount);
        }
        existing.gates.forEach((g, i) => { g.gate = `PH${i + 1}`; });
      }
    }

    // Init percentages dynamically from gate labels
    const allGateNames = new Set<string>();
    for (const tg of timeGates.value) {
      for (const g of tg.gates) {
        allGateNames.add(g.gate);
      }
    }
    const pcts: Record<string, number> = {};
    for (const name of allGateNames) {
      pcts[name] = percentages.value[name] ?? 0;
    }
    percentages.value = pcts;

    // Fetch reference from template if template_id is set
    if (data.template_id) {
      await fetchTemplateReference(data.template_id);
    }
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

async function fetchTemplateReference(templateId: string) {
  try {
    const response = await fetch(`/api/templates/${templateId}`, {
      headers: getAuthHeaders(),
    });
    if (response.ok) {
      const tpl = await response.json();
      referenceTimeGates.value = tpl.time_gates ?? [];
    }
  } catch {
    /* ignore — reference will be empty */
  }
}

function getReferenceGates(courseNumber: number): Gate[] {
  const entry = referenceTimeGates.value.find(
    (tg) => tg.course_number === courseNumber
  );
  return entry?.gates ?? [];
}

function getGatesForCourse(courseNumber: number): Gate[] {
  const entry = timeGates.value.find((tg) => tg.course_number === courseNumber);
  return entry?.gates ?? [];
}

function applyPercentages() {
  for (const courseTg of timeGates.value) {
    const refEntry = referenceTimeGates.value.find(
      (tg) => tg.course_number === courseTg.course_number
    );
    if (!refEntry) continue;

    for (const gate of courseTg.gates) {
      const refGate = refEntry.gates.find((g) => g.gate === gate.gate);
      if (!refGate) continue;
      const pct = percentages.value[gate.gate] ?? 0;
      const factor = 1 + pct / 100;

      gate.min_m =
        refGate.min_m != null ? Math.floor(refGate.min_m * factor) : null;
      gate.max_m =
        refGate.max_m != null ? Math.ceil(refGate.max_m * factor) : null;
      gate.min_f =
        refGate.min_f != null ? Math.floor(refGate.min_f * factor) : null;
      gate.max_f =
        refGate.max_f != null ? Math.ceil(refGate.max_f * factor) : null;
    }
  }
}

function resetFromTemplate(courseNumber: number) {
  const refEntry = referenceTimeGates.value.find(
    (tg) => tg.course_number === courseNumber
  );
  if (!refEntry) return;
  const target = timeGates.value.find((tg) => tg.course_number === courseNumber);
  if (target) {
    target.gates = JSON.parse(JSON.stringify(refEntry.gates));
  }
}

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await fetch(`/api/events/${props.eventId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ time_gates: timeGates.value }),
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

onMounted(fetchEvent);
</script>

<template>
  <div class="time-gates-tab">
    <div v-if="courses.length === 0" class="empty">
      Aucun parcours défini. Créez d'abord des parcours dans l'onglet
      <strong>Parcours</strong>.
    </div>

    <div v-else>
      <!-- Per-course sections -->
      <section
        v-for="course in courses"
        :key="course.number"
        class="course-section"
      >
        <h3>Parcours {{ course.number }}</h3>

        <!-- Reference table (read-only) -->
        <div v-if="getReferenceGates(course.number).length > 0" class="ref-block">
          <p class="ref-label">Temps de référence (template) :</p>
          <table class="tg-table ref-table">
            <thead>
              <tr>
                <th>PH</th>
                <th>Min (H)</th>
                <th>Max (H)</th>
                <th>Min (F)</th>
                <th>Max (F)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="gate in getReferenceGates(course.number)" :key="gate.gate">
                <td class="ph-label">{{ gate.gate }}</td>
                <td>{{ gate.min_m ?? "—" }}</td>
                <td>{{ gate.max_m ?? "—" }}</td>
                <td>{{ gate.min_f ?? "—" }}</td>
                <td>{{ gate.max_f ?? "—" }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Adjusted table (editable) -->
        <p class="adj-label">Temps ajustés (cet événement) :</p>
        <table class="tg-table">
          <thead>
            <tr>
              <th>PH</th>
              <th>Min (H)</th>
              <th>Max (H)</th>
              <th>Min (F)</th>
              <th>Max (F)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="gate in getGatesForCourse(course.number)" :key="gate.gate">
              <td class="ph-label">{{ gate.gate }}</td>
              <td>
                <input
                  v-model.number="gate.min_m"
                  type="number"
                  min="0"
                  placeholder="—"
                  class="input-time"
                />
              </td>
              <td>
                <input
                  v-model.number="gate.max_m"
                  type="number"
                  min="0"
                  placeholder="min"
                  class="input-time"
                />
              </td>
              <td>
                <input
                  v-model.number="gate.min_f"
                  type="number"
                  min="0"
                  placeholder="—"
                  class="input-time"
                />
              </td>
              <td>
                <input
                  v-model.number="gate.max_f"
                  type="number"
                  min="0"
                  placeholder="min"
                  class="input-time"
                />
              </td>
            </tr>
          </tbody>
        </table>

        <button
          v-if="getReferenceGates(course.number).length > 0"
          type="button"
          class="btn-reset"
          @click="resetFromTemplate(course.number)"
        >
          Réinitialiser depuis le template
        </button>
      </section>

      <!-- Percentage adjustment block -->
      <section v-if="referenceTimeGates.length > 0" class="pct-section">
        <h4>Ajustement par pourcentage</h4>
        <div class="pct-grid">
          <div v-for="ph in Object.keys(percentages)" :key="ph" class="pct-item">
            <label>{{ ph }}</label>
            <div class="pct-input-wrap">
              <input
                v-model.number="percentages[ph]"
                type="number"
                class="input-pct"
              />
              <span>%</span>
            </div>
          </div>
        </div>
        <button type="button" class="btn-apply" @click="applyPercentages">
          Appliquer les pourcentages
        </button>
      </section>

      <p v-if="error" class="msg error">{{ error }}</p>
      <p v-if="success" class="msg success">{{ success }}</p>

      <div class="actions">
        <button
          type="button"
          class="btn-save"
          :disabled="saving"
          @click="handleSave"
        >
          {{ saving ? "Enregistrement…" : "Enregistrer" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.time-gates-tab {
  overflow-x: auto;
}

.empty {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-style: italic;
}

.course-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: #333;
}

.ref-block {
  margin-bottom: 1rem;
}

.ref-label,
.adj-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 0.5rem;
}

.tg-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.75rem;
}

.ref-table td {
  color: #888;
  font-style: italic;
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

.ph-label {
  font-weight: 600;
  color: #1976d2;
}

.input-time {
  width: 70px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: right;
}

.btn-reset {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  background: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: 4px;
  cursor: pointer;
  color: #e65100;
}

.btn-reset:hover {
  background: #ffe0b2;
}

/* Percentage section */
.pct-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: #333;
}

.pct-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.pct-item label {
  font-size: 0.8125rem;
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
}

.pct-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.input-pct {
  width: 60px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: right;
}

.btn-apply {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
  border-radius: 4px;
  cursor: pointer;
  color: #2e7d32;
}

.btn-apply:hover {
  background: #c8e6c9;
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
  align-items: center;
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

