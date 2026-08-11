<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuth } from "../../../composables/useAuth";

interface Participant {
  first_name: string;
  last_name: string;
  sex: string;
  phone: string;
  routechoices_id: string;
  routechoices_short_name: string;
}

const props = defineProps<{ eventId: string }>();

const participants = ref<Participant[]>([]);
const saving = ref(false);
const error = ref("");
const success = ref("");
const csvInput = ref<HTMLInputElement | null>(null);
const { getAuthHeaders } = useAuth();

async function fetchParticipants() {
  try {
    const response = await fetch(`/api/events/${props.eventId}/registrations`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      error.value = "Impossible de charger les participants";
      return;
    }
    const data = await response.json();
    participants.value = data.map((p: any) => ({
      first_name: p.first_name,
      last_name: p.last_name,
      sex: p.sex,
      phone: p.phone,
      routechoices_id: p.routechoices_id || "",
      routechoices_short_name: p.routechoices_short_name || "",
    }));
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

function addParticipant() {
  participants.value.push({ first_name: "", last_name: "", sex: "H", phone: "", routechoices_id: "", routechoices_short_name: "" });
}

function removeParticipant(index: number) {
  participants.value.splice(index, 1);
}

function triggerCsvImport() {
  csvInput.value?.click();
}

function handleCsvFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target?.result as string;
    parseCsvAndMerge(text);
  };
  reader.readAsText(file, "UTF-8");

  // Reset input so the same file can be re-imported
  input.value = "";
}

function detectSeparator(headerLine: string): string {
  return headerLine.includes(";") ? ";" : ",";
}

function normalizeHeader(header: string): string {
  return header.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

const COLUMN_MAP: Record<string, keyof Participant> = {
  nom: "last_name",
  prenom: "first_name",
  sexe: "sex",
  telephone: "phone",
  "id routechoices": "routechoices_id",
  "rc short name": "routechoices_short_name",
};

function parseCsvAndMerge(text: string) {
  error.value = "";
  success.value = "";

  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  if (lines.length < 2) {
    error.value = "Le fichier CSV est vide ou ne contient qu'un en-tête";
    return;
  }

  const separator = detectSeparator(lines[0]);
  const rawHeaders = lines[0].split(separator).map(normalizeHeader);

  // Map CSV columns to Participant fields
  const columnIndices: Partial<Record<keyof Participant, number>> = {};
  for (let i = 0; i < rawHeaders.length; i++) {
    const field = COLUMN_MAP[rawHeaders[i]];
    if (field) {
      columnIndices[field] = i;
    }
  }

  // Validate all required columns are present
  const requiredColumns: (keyof Participant)[] = ["last_name", "first_name", "sex", "phone", "routechoices_id"];
  const missing = requiredColumns.filter((col) => columnIndices[col] === undefined);
  if (missing.length > 0) {
    const labels: Record<string, string> = {
      last_name: "Nom",
      first_name: "Prénom",
      sex: "Sexe",
      phone: "Téléphone",
      routechoices_id: "ID Routechoices",
    };
    error.value = `Colonnes manquantes dans le CSV : ${missing.map((m) => labels[m]).join(", ")}`;
    return;
  }

  // Parse rows
  const imported: Participant[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(separator);
    const entry: Participant = {
      last_name: cols[columnIndices.last_name!]?.trim() || "",
      first_name: cols[columnIndices.first_name!]?.trim() || "",
      sex: cols[columnIndices.sex!]?.trim().toUpperCase() || "H",
      phone: cols[columnIndices.phone!]?.trim() || "",
      routechoices_id: cols[columnIndices.routechoices_id!]?.trim() || "",
      routechoices_short_name: columnIndices.routechoices_short_name !== undefined
        ? cols[columnIndices.routechoices_short_name]?.trim() || ""
        : "",
    };
    // Skip rows without name
    if (entry.first_name && entry.last_name) {
      imported.push(entry);
    }
  }

  if (imported.length === 0) {
    error.value = "Aucun participant valide trouvé dans le fichier";
    return;
  }

  // Merge with existing participants (dedup by routechoices_id then name)
  mergeParticipants(imported);
  success.value = `${imported.length} participant(s) importé(s)`;
  setTimeout(() => (success.value = ""), 3000);
}

function mergeParticipants(imported: Participant[]) {
  const current = [...participants.value];

  for (const entry of imported) {
    let existingIndex = -1;

    // Priority: match by routechoices_id
    if (entry.routechoices_id) {
      existingIndex = current.findIndex(
        (p) => p.routechoices_id && p.routechoices_id === entry.routechoices_id
      );
    }

    // Fallback: match by first_name + last_name
    if (existingIndex === -1) {
      existingIndex = current.findIndex(
        (p) =>
          p.first_name.toLowerCase() === entry.first_name.toLowerCase() &&
          p.last_name.toLowerCase() === entry.last_name.toLowerCase()
      );
    }

    if (existingIndex !== -1) {
      // Update existing entry
      current[existingIndex] = entry;
    } else {
      // Add new entry
      current.push(entry);
    }
  }

  participants.value = current;
}

async function handleSave() {
  error.value = "";
  success.value = "";

  // Filter out empty rows
  const toSave = participants.value.filter(
    (p) => p.first_name.trim() && p.last_name.trim()
  );

  saving.value = true;
  try {
    const response = await fetch(`/api/events/${props.eventId}/registrations`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify(toSave),
    });
    if (!response.ok) {
      error.value = "Erreur lors de la sauvegarde";
      return;
    }
    const data = await response.json();
    participants.value = data.map((p: any) => ({
      first_name: p.first_name,
      last_name: p.last_name,
      sex: p.sex,
      phone: p.phone,
      routechoices_id: p.routechoices_id || "",
      routechoices_short_name: p.routechoices_short_name || "",
    }));
    success.value = "Enregistré";
    setTimeout(() => (success.value = ""), 2000);
  } catch {
    error.value = "Impossible de contacter le serveur";
  } finally {
    saving.value = false;
  }
}

onMounted(fetchParticipants);
</script>

<template>
  <div class="participants-tab">
    <table class="ptable">
      <thead>
        <tr>
          <th>Nom</th>
          <th>Prénom</th>
          <th>Sexe</th>
          <th>Téléphone</th>
          <th>ID Routechoices</th>
          <th>RC Short Name</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(p, index) in participants" :key="index">
          <td>
            <input v-model="p.last_name" type="text" placeholder="Nom" class="input-cell" />
          </td>
          <td>
            <input v-model="p.first_name" type="text" placeholder="Prénom" class="input-cell" />
          </td>
          <td>
            <select v-model="p.sex" class="select-cell">
              <option value="H">H</option>
              <option value="F">F</option>
            </select>
          </td>
          <td>
            <input v-model="p.phone" type="text" placeholder="06 ..." class="input-cell" />
          </td>
          <td>
            <input v-model="p.routechoices_id" type="text" placeholder="rc_..." class="input-cell" />
          </td>
          <td>
            <input v-model="p.routechoices_short_name" type="text" placeholder="short name" class="input-cell" />
          </td>
          <td>
            <button
              type="button"
              class="btn-delete"
              title="Supprimer"
              @click="removeParticipant(index)"
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
      <button type="button" class="btn-add" @click="addParticipant">
        + Ajouter un participant
      </button>
      <button type="button" class="btn-import" @click="triggerCsvImport">
        Importer CSV
      </button>
      <button type="button" class="btn-save" :disabled="saving" @click="handleSave">
        {{ saving ? "Enregistrement…" : "Enregistrer" }}
      </button>
    </div>

    <input
      ref="csvInput"
      type="file"
      accept=".csv"
      class="hidden"
      @change="handleCsvFile"
    />
  </div>
</template>

<style scoped>
.participants-tab {
  overflow-x: auto;
}

.ptable {
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

.input-cell {
  width: 100%;
  padding: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.select-cell {
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

.btn-import {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-import:hover {
  background: #d0d0d0;
}

.hidden {
  display: none;
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
