<script setup lang="ts">
import type { CompetitorBeacon } from "../../types/competitor";
import type { BeaconInput } from "../../types/log";
import { formatIsoToHms } from "../../utils/date";
import { hasCodeChanged, hasTimeChanged } from "../../utils/beacon-validation";

const props = defineProps<{
  beacons: CompetitorBeacon[];
  inputs: BeaconInput[];
  savingBIdx: number | null;
  phArrivalInputs?: Record<number, string>; // sequence -> HH:MM:SS input value
}>();

function phLabel(bIdx: number): string {
  let phIndex = 0;
  for (let i = 0; i <= bIdx; i++) {
    if (props.beacons[i].is_ph) phIndex++;
  }
  return `PH${phIndex}`;
}

function isLastPh(bIdx: number): boolean {
  if (!props.beacons[bIdx].is_ph) return false;
  for (let i = bIdx + 1; i < props.beacons.length; i++) {
    if (props.beacons[i].is_ph) return false;
  }
  return true;
}

const emit = defineEmits<{
  save: [bIdx: number];
  cancel: [bIdx: number];
  "fill-time": [bIdx: number];
  "save-ph-arrival": [bIdx: number];
  "cancel-ph-arrival": [bIdx: number];
  "fill-ph-arrival-time": [bIdx: number];
}>();

function hasChanged(bIdx: number): boolean {
  const beacon = props.beacons[bIdx];
  const input = props.inputs[bIdx];
  if (!input) return false;

  if (hasCodeChanged(input.code, beacon.enteredCode || "")) return true;

  const oldTime = formatIsoToHms(beacon.passageTime);
  return hasTimeChanged(input.time, oldTime);
}

function hasPhArrivalChanged(bIdx: number): boolean {
  const beacon = props.beacons[bIdx];
  if (!beacon.is_ph || !props.phArrivalInputs) return false;
  const currentInput = props.phArrivalInputs[beacon.sequence] ?? "";
  const originalTime = formatIsoToHms(beacon.phArrivalTime);
  return currentInput.trim() !== originalTime;
}
</script>

<template>
  <div v-if="beacons.length > 0" class="section-beacons">
    <table class="beacon-table">
      <thead>
        <tr>
          <th>N°</th>
          <th>PH</th>
          <th>Code</th>
          <th>Valide</th>
          <th>Heure</th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(beacon, bIdx) in beacons" :key="beacon.sequence">
          <!-- PH Arrival row (orange) — shown for non-last PHs only -->
          <tr v-if="beacon.is_ph && phArrivalInputs && !isLastPh(bIdx)" class="ph-arrival-row">
            <td>{{ beacon.beaconNumber }}</td>
            <td>{{ phLabel(bIdx) }} (arrivée)</td>
            <td>—</td>
            <td>—</td>
            <td>
              <input
                :value="phArrivalInputs[beacon.sequence] ?? ''"
                type="text"
                placeholder="HH:MM:SS"
                pattern="[0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
                class="edit-input edit-input-time"
                @input="($event: Event) => { if (phArrivalInputs) phArrivalInputs[beacon.sequence] = ($event.target as HTMLInputElement).value }"
                @click.stop
                @keydown.enter="emit('save-ph-arrival', bIdx)"
              />
            </td>
            <td>
              <button
                class="time-now-btn"
                title="Heure actuelle"
                @click.stop="emit('fill-ph-arrival-time', bIdx)"
              >⏱</button>
            </td>
            <td>
              <button
                :class="['row-save-btn', { active: hasPhArrivalChanged(bIdx) }]"
                :disabled="!hasPhArrivalChanged(bIdx)"
                title="Enregistrer l'arrivée PH"
                @click.stop="emit('save-ph-arrival', bIdx)"
              >✓</button>
              <button
                v-if="hasPhArrivalChanged(bIdx)"
                class="row-cancel-btn"
                title="Annuler"
                @click.stop="emit('cancel-ph-arrival', bIdx)"
              >✗</button>
            </td>
          </tr>
          <!-- Normal / PH departure row (green for PH) — always shown (including last PH) -->
          <tr :class="{ 'ph-departure-row': beacon.is_ph && phArrivalInputs }">
            <td>{{ beacon.beaconNumber }}</td>
            <td>
              <template v-if="beacon.is_ph && phArrivalInputs && !isLastPh(bIdx)">{{ phLabel(bIdx) }} (départ)</template>
              <template v-else>{{ beacon.is_ph ? phLabel(bIdx) : "" }}</template>
            </td>
            <td>
              <input
                v-if="inputs[bIdx]"
                v-model="inputs[bIdx].code"
                type="text"
                maxlength="2"
                placeholder="--"
                class="edit-input edit-input-code"
                @click.stop
                @keydown.enter="emit('save', bIdx)"
              />
              <span v-else>--</span>
            </td>
            <td>
              <template v-if="beacon.enteredCode">
                {{ beacon.valid === true ? "✅" : beacon.valid === false ? "❌" : "--" }}
              </template>
              <template v-else>--</template>
            </td>
            <td>
              <input
                v-if="inputs[bIdx]"
                v-model="inputs[bIdx].time"
                type="text"
                placeholder="HH:MM:SS"
                pattern="[0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
                class="edit-input edit-input-time"
                @click.stop
                @keydown.enter="emit('save', bIdx)"
              />
              <span v-else>{{ formatIsoToHms(beacon.passageTime) }}</span>
            </td>
            <td>
              <button
                v-if="inputs[bIdx]"
                class="time-now-btn"
                title="Heure actuelle"
                @click.stop="emit('fill-time', bIdx)"
              >⏱</button>
            </td>
            <td>
              <button
                v-if="inputs[bIdx]"
                :class="['row-save-btn', { active: hasChanged(bIdx) }]"
                :disabled="!hasChanged(bIdx) || savingBIdx === bIdx"
                title="Enregistrer cette ligne"
                @click.stop="emit('save', bIdx)"
              >✓</button>
              <button
                v-if="inputs[bIdx] && hasChanged(bIdx)"
                class="row-cancel-btn"
                title="Annuler"
                @click.stop="emit('cancel', bIdx)"
              >✗</button>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.beacon-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.beacon-table th,
.beacon-table td {
  padding: 0.3rem 0.4rem;
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
  padding: 0.2rem 0.3rem;
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

.row-cancel-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  line-height: 1;
  color: #e53935;
  margin-left: 0.2rem;
}

.row-cancel-btn:hover {
  background-color: #ffebee;
  border-color: #e53935;
}
</style>

