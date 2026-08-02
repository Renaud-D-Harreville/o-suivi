<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useAuth } from "../../../composables/useAuth";

const TAG_OPTIONS = ["unique", "N", "E", "S", "O", "NO", "NE", "SE", "SO"];

const MIN_BEACON_ID = 31;

interface Beacon {
  id: number;
  number: number | null;
  tag: string;
  is_ph: boolean;
  code: string;
}

const props = defineProps<{ eventId: string }>();

const beacons = ref<Beacon[]>([]);
const saving = ref(false);
const error = ref("");
const success = ref("");
const { getAuthHeaders } = useAuth();

function nextBeaconId(): number {
  if (beacons.value.length === 0) return MIN_BEACON_ID;
  return Math.max(...beacons.value.map((b) => b.id)) + 1;
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
    beacons.value = data.beacons.length
      ? data.beacons.map((b: any) => ({ ...b, is_ph: b.is_ph ?? false, code: b.code ?? "" }))
      : [{ id: MIN_BEACON_ID, number: 1, tag: "unique", is_ph: false, code: "" }];
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

function addBeacon() {
  const lastNumber =
    beacons.value.length > 0
      ? Math.max(...beacons.value.map((b) => b.number ?? 0))
      : 0;
  beacons.value.push({ id: nextBeaconId(), number: lastNumber + 1, tag: "unique", is_ph: false, code: "" });
}

function removeBeacon(index: number) {
  beacons.value.splice(index, 1);
}


/** Check if a code is duplicated. */
const duplicateCodes = computed(() => {
  const codes = beacons.value
    .map((b) => b.code.toUpperCase())
    .filter((c) => c.length === 2);
  const seen = new Set<string>();
  const dupes = new Set<string>();
  for (const c of codes) {
    if (seen.has(c)) dupes.add(c);
    seen.add(c);
  }
  return dupes;
});

function isCodeDuplicate(code: string): boolean {
  return code.length === 2 && duplicateCodes.value.has(code.toUpperCase());
}

function formatCode(beacon: Beacon) {
  beacon.code = beacon.code.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 2);
}

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await fetch(`/api/events/${props.eventId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ beacons: beacons.value }),
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
  <div class="beacons-tab">
    <table v-if="beacons.length" class="beacon-table">
      <thead>
        <tr>
          <th>N°</th>
          <th>ID</th>
          <th>Tag</th>
          <th>PH</th>
          <th>Code</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(beacon, index) in beacons" :key="index">
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
              v-model="beacon.code"
              type="text"
              maxlength="2"
              class="input-code"
              :class="{ 'code-error': isCodeDuplicate(beacon.code) }"
              placeholder="AB"
              @input="formatCode(beacon)"
            />
          </td>
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

    <p v-if="duplicateCodes.size > 0" class="msg warning">
      ⚠️ Codes en doublon : {{ [...duplicateCodes].join(", ") }}
    </p>
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

.input-code {
  width: 50px;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-transform: uppercase;
  text-align: center;
  font-weight: 600;
}

.code-error {
  border-color: #d32f2f;
  background: #fce4ec;
}

.id-cell {
  color: #999;
  font-size: 0.8125rem;
  font-family: monospace;
}

select {
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
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

.warning {
  color: #e65100;
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

