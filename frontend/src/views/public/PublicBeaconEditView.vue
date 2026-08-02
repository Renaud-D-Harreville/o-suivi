<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { formatIsoToHms, hmsToIsoTimestamp, toLocalISO, formatTime } from "../../utils/date";

const route = useRoute();
const router = useRouter();
const eventId = route.params.id as string;
const userId = route.params.userId as string;

// --- Types ---

interface CheckpointEntry {
  sequence: number;
  code: string | null;
  passage_time: string | null;
}

interface CheckpointData {
  checkpoints: CheckpointEntry[];
  ph_arrivals: Record<number, string>;
}

// --- Row model for the table ---

interface BeaconRow {
  sequence: number;
  beaconNumber: number;
  tag: string;
  phLabel: string; // "PH1", "PH2", ... or "" if not a PH
  isPh: boolean;
  isArrivalRow: boolean; // true = PH arrival line, false = normal/departure line
  code: string;
  time: string;
  originalCode: string;
  originalTime: string;
}

// --- State ---

const eventName = ref("");
const competitorName = ref("");
const rows = ref<BeaconRow[]>([]);
const loading = ref(true);
const savingIdx = ref<number | null>(null);

// --- Fetch data ---

async function fetchData() {
  try {
    // Fetch results to get event name, competitor name, and course beacons
    const [resultsRes, checkpointsRes] = await Promise.all([
      fetch(`/api/public/events/${eventId}/resultats`),
      fetch(`/api/public/events/${eventId}/competitors/${userId}/checkpoints`),
    ]);

    if (!resultsRes.ok || !checkpointsRes.ok) return;

    const resultsData = await resultsRes.json();
    const checkpointData: CheckpointData = await checkpointsRes.json();

    // Find competitor
    const comp = resultsData.competitors.find((c: any) => c.user_id === userId);
    if (!comp) return;

    eventName.value = "Résultats";
    competitorName.value = `${comp.first_name} ${comp.last_name}`;

    // Build rows from competitor beacons (from results)
    const beacons = comp.beacons as Array<{
      sequence: number;
      beacon_number: number;
      tag: string;
      is_ph: boolean;
      entered_code: string | null;
    }>;

    const cpMap = new Map<number, CheckpointEntry>();
    for (const cp of checkpointData.checkpoints) {
      cpMap.set(cp.sequence, cp);
    }

    // Compute PH labels dynamically
    let phIndex = 0;
    const phLabels = new Map<number, string>();
    for (const b of beacons) {
      if (b.is_ph) {
        phIndex++;
        phLabels.set(b.sequence, `PH${phIndex}`);
      }
    }

    // Determine last PH sequence
    let lastPhSequence: number | null = null;
    for (let i = beacons.length - 1; i >= 0; i--) {
      if (beacons[i].is_ph) {
        lastPhSequence = beacons[i].sequence;
        break;
      }
    }

    const builtRows: BeaconRow[] = [];
    for (const b of beacons) {
      const cp = cpMap.get(b.sequence);
      const isPh = b.is_ph;
      const label = phLabels.get(b.sequence) || "";
      const isLast = b.sequence === lastPhSequence;

      if (isPh && isLast) {
        // Last PH: single departure/validation row (code + time, no arrival row)
        const enteredCode = cp?.code || b.entered_code || "";
        const passageTime = cp?.passage_time || null;
        const timeHms = formatIsoToHms(passageTime);
        builtRows.push({
          sequence: b.sequence,
          beaconNumber: b.beacon_number,
          tag: b.tag,
          phLabel: label,
          isPh: true,
          isArrivalRow: false,
          code: enteredCode,
          time: timeHms,
          originalCode: enteredCode,
          originalTime: timeHms,
        });
      } else if (isPh) {
        // Non-last PH: arrival row + departure row
        const arrivalTime = checkpointData.ph_arrivals[b.sequence] || null;
        const arrivalHms = formatIsoToHms(arrivalTime);
        builtRows.push({
          sequence: b.sequence,
          beaconNumber: b.beacon_number,
          tag: b.tag,
          phLabel: label,
          isPh: true,
          isArrivalRow: true,
          code: "",
          time: arrivalHms,
          originalCode: "",
          originalTime: arrivalHms,
        });

        // Departure row
        const enteredCode = cp?.code || b.entered_code || "";
        const passageTime = cp?.passage_time || null;
        const timeHms = formatIsoToHms(passageTime);
        builtRows.push({
          sequence: b.sequence,
          beaconNumber: b.beacon_number,
          tag: b.tag,
          phLabel: label,
          isPh: true,
          isArrivalRow: false,
          code: enteredCode,
          time: timeHms,
          originalCode: enteredCode,
          originalTime: timeHms,
        });
      } else {
        // Normal beacon: single row
        const enteredCode = cp?.code || b.entered_code || "";
        const passageTime = cp?.passage_time || null;
        const timeHms = formatIsoToHms(passageTime);
        builtRows.push({
          sequence: b.sequence,
          beaconNumber: b.beacon_number,
          tag: b.tag,
          phLabel: label,
          isPh: false,
          isArrivalRow: false,
          code: enteredCode,
          time: timeHms,
          originalCode: enteredCode,
          originalTime: timeHms,
        });
      }
    }

    rows.value = builtRows;
  } catch (err) {
    console.error("Failed to fetch beacon data:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

// --- Helpers ---

function hasChanged(idx: number): boolean {
  const row = rows.value[idx];
  if (!row) return false;

  if (row.isArrivalRow) {
    return row.time.trim() !== row.originalTime;
  }

  const newCode = row.code.toUpperCase().trim();
  const oldCode = row.originalCode.toUpperCase();
  const codeValid = newCode.length === 0 || newCode.length === 2;
  if (newCode !== oldCode && codeValid) return true;

  const newTime = row.time.trim();
  return newTime !== row.originalTime;
}

async function saveRow(idx: number): Promise<void> {
  const row = rows.value[idx];
  if (!row || !hasChanged(idx)) return;

  savingIdx.value = idx;
  try {
    const creation_date = toLocalISO(new Date());

    if (row.isArrivalRow) {
      // Save PH arrival time via dedicated ph-arrival-edit endpoint
      const passage_time = hmsToIsoTimestamp(row.time.trim()) || null;
      const res = await fetch(
        `/api/public/events/${eventId}/competitors/${userId}/ph-arrival-edit`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ creation_date, passage_time, sequence: row.sequence }),
        },
      );
      if (res.ok) {
        row.originalTime = row.time;
      }
    } else {
      // Save code + passage time
      const newCode = row.code.toUpperCase().trim();
      const codeToSend = newCode.length === 2 ? newCode : null;
      const passage_time = hmsToIsoTimestamp(row.time.trim()) || null;

      const res = await fetch(
        `/api/public/events/${eventId}/competitors/${userId}/checkpoint-edit`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ creation_date, passage_time, sequence: row.sequence, code: codeToSend }),
        },
      );
      if (res.ok) {
        row.originalCode = row.code;
        row.originalTime = row.time;
      }
    }
  } finally {
    savingIdx.value = null;
  }
}

function fillCurrentTime(idx: number): void {
  const row = rows.value[idx];
  if (row) {
    row.time = formatTime(new Date());
  }
}

function goBack() {
  router.push(`/events/${eventId}`);
}
</script>

<template>
  <div class="public-beacon-edit-view">
    <header class="edit-header">
      <button class="back-btn" @click="goBack">← Retour aux résultats</button>
      <h1>{{ competitorName }}</h1>
    </header>

    <main class="content">
      <div v-if="loading" class="loading">Chargement…</div>

      <div v-else-if="rows.length === 0" class="empty">Aucune balise trouvée.</div>

      <table v-else class="beacon-table">
        <thead>
          <tr>
            <th>N°</th>
            <th>PH</th>
            <th>Code</th>
            <th>Heure</th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in rows"
            :key="`${row.sequence}-${row.isArrivalRow}`"
            :class="{
              'ph-arrival-row': row.isArrivalRow,
              'ph-departure-row': row.isPh && !row.isArrivalRow,
            }"
          >
            <td>{{ row.beaconNumber }}</td>
            <td>
              <template v-if="row.isArrivalRow">{{ row.phLabel }} (arrivée)</template>
              <template v-else>{{ row.phLabel }}</template>
            </td>
            <td>
              <template v-if="row.isArrivalRow">—</template>
              <input
                v-else
                v-model="row.code"
                type="text"
                maxlength="2"
                placeholder="--"
                class="edit-input edit-input-code"
                @keydown.enter="saveRow(idx)"
              />
            </td>
            <td>
              <input
                v-model="row.time"
                type="text"
                placeholder="HH:MM:SS"
                pattern="[0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
                class="edit-input edit-input-time"
                @keydown.enter="saveRow(idx)"
              />
            </td>
            <td>
              <button
                class="time-now-btn"
                title="Heure actuelle"
                @click="fillCurrentTime(idx)"
              >⏱</button>
            </td>
            <td>
              <button
                :class="['row-save-btn', { active: hasChanged(idx) }]"
                :disabled="!hasChanged(idx) || savingIdx === idx"
                title="Enregistrer cette ligne"
                @click="saveRow(idx)"
              >✓</button>
            </td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.public-beacon-edit-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.edit-header {
  background: #1976d2;
  color: #fff;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  background: rgba(255,255,255,0.15);
  border: none;
  color: #fff;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.back-btn:hover {
  background: rgba(255,255,255,0.25);
}

.edit-header h1 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.content {
  padding: 1rem;
  max-width: 700px;
  margin: 0 auto;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.beacon-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.beacon-table th,
.beacon-table td {
  padding: 0.4rem 0.5rem;
  border: 1px solid #e0e0e0;
  text-align: center;
}

.beacon-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.ph-arrival-row {
  background: #fff3e0;
}

.ph-departure-row {
  background: #e8f5e9;
}

.edit-input {
  padding: 0.25rem 0.3rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.8rem;
}

.edit-input-code {
  width: 36px;
  text-transform: uppercase;
  text-align: center;
}

.edit-input-time {
  width: 72px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.time-now-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.15rem 0.3rem;
  line-height: 1;
}

.time-now-btn:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

.row-save-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: default;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  line-height: 1;
  color: #ccc;
}

.row-save-btn.active {
  color: #fff;
  background-color: #4caf50;
  border-color: #4caf50;
  cursor: pointer;
}

.row-save-btn.active:hover {
  background-color: #388e3c;
  border-color: #388e3c;
}

.row-save-btn:disabled {
  cursor: default;
  opacity: 0.5;
}
</style>


