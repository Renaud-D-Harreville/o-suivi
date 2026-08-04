<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { CompetitorBeacon } from "../../types/competitor";
import type { BeaconInput } from "../../types/log";
import { formatIsoToHms, hmsToIsoTimestamp, toLocalISO, formatTime } from "../../utils/date";
import { hasCodeChanged, hasTimeChanged, codeToPayload } from "../../utils/beacon-validation";
import { apiFetch } from "../../utils/api";
import { shortName } from "../../utils/format";
import BeaconEditTable from "../../components/suivi/BeaconEditTable.vue";
import AdminBackLink from "../../components/AdminBackLink.vue";

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

// --- State ---

const competitorName = ref("");
const beacons = ref<CompetitorBeacon[]>([]);
const inputs = ref<BeaconInput[]>([]);
const phArrivalInputs = reactive<Record<number, string>>({});
const loading = ref(true);
const savingBIdx = ref<number | null>(null);

// --- Fetch data ---

async function fetchData() {
  try {
    const [resultsRes, checkpointsRes] = await Promise.all([
      fetch(`/api/public/events/${eventId}/resultats`),
      fetch(`/api/public/events/${eventId}/competitors/${userId}/checkpoints`),
    ]);

    if (!resultsRes.ok || !checkpointsRes.ok) return;

    const resultsData = await resultsRes.json();
    const checkpointData: CheckpointData = await checkpointsRes.json();

    const comp = resultsData.competitors.find((c: any) => c.user_id === userId);
    if (!comp) return;

    competitorName.value = shortName(comp.first_name, comp.last_name);

    const rawBeacons = comp.beacons as Array<{
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

    const builtBeacons: CompetitorBeacon[] = [];
    const builtInputs: BeaconInput[] = [];

    for (const b of rawBeacons) {
      const cp = cpMap.get(b.sequence);
      const enteredCode = cp?.code || b.entered_code || null;
      const passageTime = cp?.passage_time || null;
      const phArrivalTime = b.is_ph ? (checkpointData.ph_arrivals[b.sequence] || null) : null;

      builtBeacons.push({
        sequence: b.sequence,
        beaconNumber: b.beacon_number,
        tag: b.tag,
        is_ph: b.is_ph,
        expectedCode: null,
        enteredCode,
        valid: null,
        passageTime,
        phArrivalTime,
      });

      builtInputs.push({
        code: enteredCode || "",
        time: formatIsoToHms(passageTime),
      });

      if (b.is_ph) {
        phArrivalInputs[b.sequence] = formatIsoToHms(phArrivalTime);
      }
    }

    beacons.value = builtBeacons;
    inputs.value = builtInputs;
  } catch (err) {
    console.error("Failed to fetch beacon data:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

// --- Save handlers ---

async function handleSave(bIdx: number): Promise<void> {
  const beacon = beacons.value[bIdx];
  const input = inputs.value[bIdx];
  if (!beacon || !input) return;

  const oldCode = beacon.enteredCode || "";
  const oldTime = formatIsoToHms(beacon.passageTime);
  const codeChanged = hasCodeChanged(input.code, oldCode);
  const timeChanged = hasTimeChanged(input.time, oldTime);
  if (!codeChanged && !timeChanged) return;

  savingBIdx.value = bIdx;
  try {
    const codeToSend = codeChanged ? codeToPayload(input.code) : (oldCode.length === 2 ? oldCode.toUpperCase() : null);
    const passage_time = hmsToIsoTimestamp(input.time.trim()) || null;
    const creation_date = toLocalISO(new Date());

    const res = await apiFetch(
      `/api/public/events/${eventId}/competitors/${userId}/checkpoint-edit`,
      {
        method: "POST",
        body: JSON.stringify({ creation_date, passage_time, sequence: beacon.sequence, code: codeToSend }),
      },
    );

    if (res.ok) {
      beacon.enteredCode = codeToSend;
      beacon.passageTime = passage_time;
      inputs.value[bIdx] = {
        code: beacon.enteredCode || "",
        time: formatIsoToHms(beacon.passageTime),
      };
    }
  } finally {
    savingBIdx.value = null;
  }
}

async function handleSavePhArrival(bIdx: number): Promise<void> {
  const beacon = beacons.value[bIdx];
  if (!beacon || !beacon.is_ph) return;

  const oldTime = formatIsoToHms(beacon.phArrivalTime);
  if (!hasTimeChanged(phArrivalInputs[beacon.sequence] || "", oldTime)) return;

  savingBIdx.value = bIdx;
  try {
    const newTime = (phArrivalInputs[beacon.sequence] || "").trim();
    const passage_time = hmsToIsoTimestamp(newTime) || null;
    const creation_date = toLocalISO(new Date());

    const res = await apiFetch(
      `/api/public/events/${eventId}/competitors/${userId}/ph-arrival-edit`,
      {
        method: "POST",
        body: JSON.stringify({ creation_date, passage_time, sequence: beacon.sequence }),
      },
    );

    if (res.ok) {
      beacon.phArrivalTime = passage_time;
      phArrivalInputs[beacon.sequence] = formatIsoToHms(beacon.phArrivalTime);
    }
  } finally {
    savingBIdx.value = null;
  }
}

function handleFillTime(bIdx: number): void {
  const input = inputs.value[bIdx];
  if (input) {
    input.time = formatTime(new Date());
  }
}

function handleFillPhArrivalTime(bIdx: number): void {
  const beacon = beacons.value[bIdx];
  if (beacon?.is_ph) {
    phArrivalInputs[beacon.sequence] = formatTime(new Date());
  }
}

function handleCancel(bIdx: number): void {
  const beacon = beacons.value[bIdx];
  if (!beacon) return;
  inputs.value[bIdx] = {
    code: beacon.enteredCode || "",
    time: formatIsoToHms(beacon.passageTime),
  };
}

function handleCancelPhArrival(bIdx: number): void {
  const beacon = beacons.value[bIdx];
  if (beacon?.is_ph) {
    phArrivalInputs[beacon.sequence] = formatIsoToHms(beacon.phArrivalTime);
  }
}

function goBack() {
  router.push(`/events/${eventId}`);
}
</script>

<template>
  <div class="public-beacon-edit-view">
    <header class="edit-header">
      <AdminBackLink :to="`/admin/events/${eventId}/suivi`" />
      <button class="back-btn" @click="goBack">← Retour aux résultats</button>
      <h1>{{ competitorName }}</h1>
    </header>

    <main class="content">
      <div v-if="loading" class="loading">Chargement…</div>

      <div v-else-if="beacons.length === 0" class="empty">Aucune balise trouvée.</div>

      <BeaconEditTable
        v-else
        :beacons="beacons"
        :inputs="inputs"
        :ph-arrival-inputs="phArrivalInputs"
        :saving-b-idx="savingBIdx"
        :show-valid="false"
        @save="handleSave"
        @cancel="handleCancel"
        @fill-time="handleFillTime"
        @save-ph-arrival="handleSavePhArrival"
        @cancel-ph-arrival="handleCancelPhArrival"
        @fill-ph-arrival-time="handleFillPhArrivalTime"
      />
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
  position: relative;
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
</style>
