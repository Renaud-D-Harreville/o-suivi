<script setup lang="ts">
import { ref, onMounted } from "vue";

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

interface Course {
  number: number;
  beacons: { id: number; number: number; tag: string; is_ph: boolean }[];
}

const props = defineProps<{ templateId: string }>();

const courses = ref<Course[]>([]);
const timeGates = ref<CourseTimeGates[]>([]);
const saving = ref(false);
const error = ref("");
const success = ref("");

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

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

async function fetchTemplate() {
  try {
    const [coursesRes, timeGatesRes] = await Promise.all([
      fetch(`/api/templates/${props.templateId}/courses`, {
        headers: getAuthHeaders(),
      }),
      fetch(`/api/templates/${props.templateId}/time-gates`, {
        headers: getAuthHeaders(),
      }),
    ]);
    if (!coursesRes.ok || !timeGatesRes.ok) {
      error.value = "Impossible de charger les données";
      return;
    }
    courses.value = await coursesRes.json();
    timeGates.value = await timeGatesRes.json();

    // Ensure each course has a time_gates entry with correct PH count
    for (const course of courses.value) {
      const existing = timeGates.value.find(
        (tg) => tg.course_number === course.number
      );
      if (!existing) {
        timeGates.value.push({
          course_number: course.number,
          gates: emptyGatesForCourse(course),
        });
      } else {
        // Adjust gate count if PH beacons changed
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
        // Ensure gate labels are correct
        existing.gates.forEach((g, i) => { g.gate = `PH${i + 1}`; });
      }
    }
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

function getGatesForCourse(courseNumber: number): Gate[] {
  const entry = timeGates.value.find((tg) => tg.course_number === courseNumber);
  return entry?.gates ?? [];
}

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await fetch(
      `/api/templates/${props.templateId}/time-gates`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(timeGates.value),
      },
    );
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

onMounted(fetchTemplate);
</script>

<template>
  <div class="time-gates-tab">
    <div v-if="courses.length === 0" class="empty">
      Aucun parcours défini. Créez d'abord des parcours dans l'onglet
      <strong>Parcours</strong>.
    </div>

    <div v-else>
      <section
        v-for="course in courses"
        :key="course.number"
        class="course-section"
      >
        <h3>Parcours {{ course.number }}</h3>
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

.tg-table {
  width: 100%;
  border-collapse: collapse;
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

