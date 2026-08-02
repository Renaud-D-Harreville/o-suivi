<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

interface Beacon {
  id: number;
  number: number;
  tag: string;
  is_ph: boolean;
}

interface Course {
  number: number;
  beacons: { number: number; tag: string }[];
}

const props = defineProps<{ templateId: string }>();

const beacons = ref<Beacon[]>([]);
const courses = ref<Course[]>([]);
const saving = ref(false);
const error = ref("");
const success = ref("");

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Distinct beacon numbers in order. */
const beaconNumbers = computed(() => {
  const seen = new Set<number>();
  const result: number[] = [];
  for (const b of beacons.value) {
    if (!seen.has(b.number)) {
      seen.add(b.number);
      result.push(b.number);
    }
  }
  return result;
});

/** For a given beacon number, return the PH label (e.g. "PH1") or null. */
function gateForNumber(num: number): string | null {
  const beacon = beacons.value.find((b) => b.number === num && b.is_ph);
  if (!beacon) return null;
  // Compute PH index: count PH beacons with number <= this one
  let phIndex = 0;
  for (const b of beacons.value) {
    if (b.is_ph) {
      phIndex++;
      if (b.number === num) return `PH${phIndex}`;
    }
  }
  return null;
}

/** Tags available for a given beacon number. If only "unique", returns ["unique"]. */
function tagsForNumber(num: number): string[] {
  return beacons.value
    .filter((b) => b.number === num)
    .map((b) => b.tag);
}

function isUnique(num: number): boolean {
  const tags = tagsForNumber(num);
  return tags.length === 1 && tags[0] === "unique";
}

/** Get the selected tag for a course at a given beacon number. */
function getSelectedTag(course: Course, num: number): string {
  const entry = course.beacons.find((b) => b.number === num);
  return entry?.tag ?? tagsForNumber(num)[0] ?? "unique";
}

/** Set the selected tag for a course at a given beacon number. */
function setSelectedTag(course: Course, num: number, tag: string) {
  const entry = course.beacons.find((b) => b.number === num);
  if (entry) {
    entry.tag = tag;
  } else {
    course.beacons.push({ number: num, tag });
  }
}

function addCourse() {
  const nextNumber =
    courses.value.length > 0
      ? Math.max(...courses.value.map((c) => c.number)) + 1
      : 1;
  const newBeacons = beaconNumbers.value.map((num) => ({
    number: num,
    tag: tagsForNumber(num)[0] ?? "unique",
  }));
  courses.value.push({ number: nextNumber, beacons: newBeacons });
}

function removeCourse(index: number) {
  courses.value.splice(index, 1);
}

async function fetchTemplate() {
  try {
    const [beaconsRes, coursesRes] = await Promise.all([
      fetch(`/api/templates/${props.templateId}/beacons`, {
        headers: getAuthHeaders(),
      }),
      fetch(`/api/templates/${props.templateId}/courses`, {
        headers: getAuthHeaders(),
      }),
    ]);
    if (!beaconsRes.ok || !coursesRes.ok) {
      error.value = "Impossible de charger les données";
      return;
    }
    beacons.value = await beaconsRes.json();
    courses.value = await coursesRes.json();
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const payload = courses.value.map((c) => ({
      number: c.number,
      beacons: c.beacons
        .map((cb) => {
          const beacon = beacons.value.find(
            (b) => b.number === cb.number && b.tag === cb.tag,
          );
          return beacon?.id;
        })
        .filter((id): id is number => id !== undefined),
    }));

    const response = await fetch(
      `/api/templates/${props.templateId}/courses`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(payload),
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
  <div class="courses-tab">
    <div v-if="beaconNumbers.length === 0" class="empty">
      Aucune balise définie. Remplissez d'abord l'onglet
      <strong>Registre balises</strong>.
    </div>

    <div v-else>
      <div class="table-wrapper">
        <table class="courses-table">
          <thead>
            <tr>
              <th>N°</th>
              <th v-for="(course, ci) in courses" :key="course.number">
                <div class="course-header">
                  <span>Parcours {{ course.number }}</span>
                  <button
                    type="button"
                    class="btn-delete-col"
                    title="Supprimer ce parcours"
                    @click="removeCourse(ci)"
                  >
                    ✕
                  </button>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="num in beaconNumbers" :key="num">
              <td class="beacon-num">
                {{ num }}
                <span v-if="gateForNumber(num)" class="gate-badge">
                  {{ gateForNumber(num) }}
                </span>
              </td>
              <td v-for="course in courses" :key="course.number">
                <span v-if="isUnique(num)" class="cell-unique">unique</span>
                <select
                  v-else
                  :value="getSelectedTag(course, num)"
                  @change="setSelectedTag(course, num, ($event.target as HTMLSelectElement).value)"
                >
                  <option
                    v-for="tag in tagsForNumber(num)"
                    :key="tag"
                    :value="tag"
                  >
                    {{ tag }}
                  </option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="error" class="msg error">{{ error }}</p>
      <p v-if="success" class="msg success">{{ success }}</p>

      <div class="actions">
        <button type="button" class="btn-add" @click="addCourse">
          + Ajouter un parcours
        </button>
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
.courses-tab {
  overflow-x: auto;
}

.empty {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-style: italic;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 1rem;
}

.courses-table {
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

.course-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-delete-col {
  background: none;
  border: none;
  color: #d32f2f;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0.125rem 0.375rem;
}

.btn-delete-col:hover {
  background: #fce4ec;
  border-radius: 4px;
}

.beacon-num {
  font-weight: 600;
  white-space: nowrap;
}

.gate-badge {
  font-size: 0.75rem;
  color: #1976d2;
  margin-left: 0.25rem;
}

.cell-unique {
  color: #999;
  font-style: italic;
  font-size: 0.8125rem;
}

select {
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
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

.btn-add {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-add:hover {
  background: #d0d0d0;
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

