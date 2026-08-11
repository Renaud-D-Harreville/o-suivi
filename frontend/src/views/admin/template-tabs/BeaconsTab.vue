<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

const TAG_OPTIONS = ["unique", "N", "E", "S", "O", "NO", "NE", "SE", "SO"];

const MIN_BEACON_ID = 31;

interface Beacon {
  id: number;
  number: number | null;
  tag: string;
  is_ph: boolean;
  coordinates: string | null;
}

const props = defineProps<{ templateId: string }>();

const beacons = ref<Beacon[]>([]);
const saving = ref(false);
const error = ref("");
const success = ref("");
let idCounter = MIN_BEACON_ID;

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function nextBeaconId(): number {
  return idCounter++;
}

async function fetchTemplate() {
  try {
    const response = await fetch(
      `/api/templates/${props.templateId}/beacons`,
      { headers: getAuthHeaders() },
    );
    if (!response.ok) {
      error.value = "Impossible de charger les balises";
      return;
    }
    const data = await response.json();
    beacons.value = data.length
      ? data
      : [{ id: MIN_BEACON_ID, number: 1, tag: "unique", is_ph: false, coordinates: null }];
    idCounter = Math.max(...beacons.value.map((b) => b.id)) + 1;
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

function addBeacon() {
  const lastNumber =
    beacons.value.length > 0
      ? Math.max(...beacons.value.map((b) => b.number ?? 0))
      : 0;
  beacons.value.push({
    id: nextBeaconId(),
    number: lastNumber + 1,
    tag: "unique",
    is_ph: false,
    coordinates: null,
  });
}

function removeBeacon(index: number) {
  beacons.value.splice(index, 1);
}

const sections = computed(() => {
  const result: number[] = [];
  let currentSection = 1;
  for (const b of beacons.value) {
    result.push(currentSection);
    if (b.is_ph) {
      currentSection++;
    }
  }
  return result;
});

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await fetch(
      `/api/templates/${props.templateId}/beacons`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(beacons.value),
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
  <div class="beacons-tab">
    <table v-if="beacons.length" class="beacon-table">
      <thead>
        <tr>
          <th>N°</th>
          <th>ID</th>
          <th>Tag</th>
          <th>PH</th>
          <th>Coordonnees</th>
          <th>Section</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(beacon, index) in beacons" :key="beacon.id">
          <td>
            <input
              v-model.number="beacon.number"
              type="number"
              min="1"
              class="input-number"
            />
          </td>
          <td class="id-cell">{{ beacon.id }}</td>
          <td>
            <select v-model="beacon.tag">
              <option v-for="opt in TAG_OPTIONS" :key="opt" :value="opt">
                {{ opt }}
              </option>
            </select>
          </td>
          <td>
            <input
              type="checkbox"
              v-model="beacon.is_ph"
              class="input-checkbox"
            />
          </td>
          <td>
            <input
              v-model="beacon.coordinates"
              type="text"
              class="input-coordinates"
              placeholder="45.883424, 5.863804"
            />
          </td>
          <td class="section-cell">Section {{ sections[index] }}</td>
          <td>
            <button
              type="button"
              class="btn-delete"
              title="Supprimer"
              @click="removeBeacon(index)"
            >
              ✕
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="error" class="msg error">{{ error }}</p>
    <p v-if="success" class="msg success">{{ success }}</p>

    <div class="actions">
      <button type="button" class="btn-add" @click="addBeacon">
        + Ajouter une balise
      </button>
      <button type="button" class="btn-save" :disabled="saving" @click="handleSave">
        {{ saving ? "Enregistrement…" : "Enregistrer" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.beacons-tab {
  overflow-x: auto;
}

.beacon-table {
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

.input-number {
  width: 60px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.input-coordinates {
  width: 200px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

select {
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.section-cell {
  color: #888;
  font-size: 0.8125rem;
  font-style: italic;
}

.id-cell {
  color: #999;
  font-size: 0.8125rem;
  font-family: monospace;
}

.btn-delete {
  background: none;
  border: none;
  color: #d32f2f;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.btn-delete:hover {
  background: #fce4ec;
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

