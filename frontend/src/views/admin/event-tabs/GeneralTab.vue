<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useAuth } from "../../../composables/useAuth";

interface TemplateSummary {
  id: string;
  name: string;
}

const props = defineProps<{ eventId: string }>();

const publicUrl = computed(() => `${window.location.origin}/events/${props.eventId}`);
const copied = ref(false);

function copyPublicLink(): void {
  navigator.clipboard.writeText(publicUrl.value);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}

const emit = defineEmits<{
  saved: [];
}>();

const { getAuthHeaders } = useAuth();
const name = ref("");
const date = ref("");
const templateId = ref<string | null>(null);
const firstStartTime = ref("");
const routechoicesUrl = ref("");
const publicRoutechoicesTime = ref("");
const gpsPollingEnabled = ref(false);
const templates = ref<TemplateSummary[]>([]);
const saving = ref(false);
const importing = ref(false);
const showImportConfirm = ref(false);
const error = ref("");
const success = ref("");

const selectedTemplateName = computed(() => {
  const tpl = templates.value.find((t) => t.id === templateId.value);
  return tpl?.name ?? "le template";
});


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
    name.value = data.name ?? "";
    date.value = data.date ?? "";
    templateId.value = data.template_id;
    firstStartTime.value = data.first_start_time ?? "";
    routechoicesUrl.value = data.routechoices_url ?? "";
    publicRoutechoicesTime.value = data.public_routechoices_time ?? "";
    gpsPollingEnabled.value = data.gps_polling_enabled ?? false;
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

async function fetchTemplates() {
  try {
    const response = await fetch("/api/templates", {
      headers: getAuthHeaders(),
    });
    if (response.ok) {
      templates.value = await response.json();
    }
  } catch {
    /* ignore — dropdown will be empty */
  }
}

async function handleSave() {
  error.value = "";
  success.value = "";
  saving.value = true;

  const payload: Record<string, string | boolean | null> = {};
  payload.name = name.value || null;
  payload.date = date.value || null;
  payload.template_id = templateId.value || null;
  payload.first_start_time = firstStartTime.value || null;
  payload.routechoices_url = routechoicesUrl.value || null;
  payload.public_routechoices_time = publicRoutechoicesTime.value || null;
  payload.gps_polling_enabled = gpsPollingEnabled.value;

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
    emit("saved");
    setTimeout(() => (success.value = ""), 2000);
  } catch {
    error.value = "Impossible de contacter le serveur";
  } finally {
    saving.value = false;
  }
}

async function handleImportTemplate() {
  showImportConfirm.value = false;
  error.value = "";
  success.value = "";
  importing.value = true;

  try {
    const response = await fetch(`/api/events/${props.eventId}/import-template`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const data = await response.json().catch(() => null);
      error.value = data?.detail ?? "Erreur lors de l'import";
      return;
    }
    success.value = "Données importées depuis le template";
    setTimeout(() => (success.value = ""), 3000);
  } catch {
    error.value = "Impossible de contacter le serveur";
  } finally {
    importing.value = false;
  }
}

onMounted(() => {
  fetchEvent();
  fetchTemplates();
});
</script>

<template>
  <form class="general-tab" @submit.prevent="handleSave">
    <div class="public-link-block">
      <label>Lien public</label>
      <div class="public-link-row">
        <a :href="publicUrl" target="_blank" class="public-link">{{ publicUrl }}</a>
        <button type="button" class="copy-btn" title="Copier le lien" @click="copyPublicLink">
          {{ copied ? "✓ Copié" : "📋 Copier" }}
        </button>
      </div>
    </div>

    <div class="field">
      <label for="event-name">Nom</label>
      <input id="event-name" v-model="name" type="text" required />
    </div>

    <div class="field">
      <label for="event-date">Date</label>
      <input id="event-date" v-model="date" type="date" />
    </div>

    <div class="field">
      <label for="event-template">Template de probatoire</label>
      <select id="event-template" v-model="templateId">
        <option :value="null">— Aucun —</option>
        <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
          {{ tpl.name }}
        </option>
      </select>
    </div>

    <div class="field">
      <label for="event-start-time">Heure du premier départ</label>
      <input id="event-start-time" v-model="firstStartTime" type="time" />
    </div>

    <div class="field">
      <label for="event-routechoices">Lien Routechoices</label>
      <input
        id="event-routechoices"
        v-model="routechoicesUrl"
        type="url"
        placeholder="https://..."
      />
    </div>

    <div class="field">
      <label for="event-routechoices-time">Routechoices public (heure d'affichage)</label>
      <div class="time-with-btn">
        <input
          id="event-routechoices-time"
          v-model="publicRoutechoicesTime"
          type="time"
        />
        <button
          type="button"
          class="time-now-btn"
          title="Heure actuelle"
          @click="publicRoutechoicesTime = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })"
        >⏱</button>
      </div>
    </div>

    <div class="field field-toggle">
      <label for="event-gps-polling">Polling GPS</label>
      <div class="toggle-row">
        <input
          id="event-gps-polling"
          v-model="gpsPollingEnabled"
          type="checkbox"
          class="toggle-checkbox"
        />
        <span class="toggle-label">{{ gpsPollingEnabled ? "Activé" : "Désactivé" }}</span>
      </div>
    </div>

    <p v-if="error" class="msg error">{{ error }}</p>
    <p v-if="success" class="msg success">{{ success }}</p>

    <div class="actions-row">
      <button type="submit" class="btn-save" :disabled="saving">
        {{ saving ? "Enregistrement…" : "Enregistrer" }}
      </button>

      <button
        v-if="templateId"
        type="button"
        class="btn-import"
        :disabled="importing"
        @click="showImportConfirm = true"
      >
        {{ importing ? "Import en cours…" : "Initialiser depuis le template" }}
      </button>
    </div>

    <!-- Confirmation popup -->
    <div v-if="showImportConfirm" class="overlay" @click.self="showImportConfirm = false">
      <div class="modal">
        <h2>Initialiser depuis le template</h2>
        <p>
          Les <strong>balises</strong>, <strong>parcours</strong> et
          <strong>barrières horaires</strong> seront réinitialisés depuis le
          template <strong>{{ selectedTemplateName }}</strong>.
        </p>
        <p class="warning-text">
          Les codes balises et les données existantes seront perdus.
        </p>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="showImportConfirm = false">
            Annuler
          </button>
          <button type="button" class="btn-confirm" @click="handleImportTemplate">
            Confirmer
          </button>
        </div>
      </div>
    </div>
  </form>
</template>

<style scoped>
.general-tab {
  max-width: 480px;
}

.public-link-block {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.public-link-block label {
  font-weight: 600;
  margin-bottom: 0.25rem;
  display: block;
}

.public-link-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.public-link {
  font-size: 0.875rem;
  color: #1976d2;
  word-break: break-all;
}

.copy-btn {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.copy-btn:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.25rem;
  font-weight: 600;
}

input,
select {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.time-with-btn {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.time-now-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.4rem 0.6rem;
  line-height: 1;
}

.time-now-btn:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

.field-toggle {
  margin-bottom: 1rem;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-checkbox {
  width: 1.1rem;
  height: 1.1rem;
  cursor: pointer;
}

.toggle-label {
  font-size: 0.875rem;
  color: #555;
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

.actions-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn-save {
  padding: 0.625rem 1.25rem;
  font-size: 1rem;
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

.btn-import {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #e65100;
  background: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: 4px;
  cursor: pointer;
}

.btn-import:hover:not(:disabled) {
  background: #ffe0b2;
}

.btn-import:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Confirmation popup */
.overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

.modal h2 {
  margin: 0 0 1rem;
  font-size: 1.125rem;
}

.modal p {
  margin: 0 0 0.75rem;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.warning-text {
  color: #d32f2f;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: #e65100;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm:hover {
  background-color: #bf360c;
}
</style>

