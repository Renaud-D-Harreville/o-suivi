<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import CreateModal from "../../components/CreateModal.vue";
import type { TemplateSummary, EventSummary } from "../../types/results";
import { apiFetch } from "../../utils/api";

const router = useRouter();

const activeTab = ref<"templates" | "events">("templates");
const templates = ref<TemplateSummary[]>([]);
const events = ref<EventSummary[]>([]);
const showModal = ref(false);
const error = ref("");


async function fetchTemplates() {
  try {
    const response = await apiFetch("/api/templates");
    if (response.status === 401) return;
    templates.value = await response.json();
  } catch {
    error.value = "Impossible de charger les templates";
  }
}

async function fetchEvents() {
  try {
    const response = await apiFetch("/api/events");
    if (response.status === 401) return;
    events.value = await response.json();
  } catch {
    error.value = "Impossible de charger les événements";
  }
}

async function handleCreate(name: string) {
  const endpoint =
    activeTab.value === "templates" ? "/api/templates" : "/api/events";
  try {
    const response = await apiFetch(endpoint, {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    if (!response.ok) {
      error.value = "Erreur lors de la création";
      return;
    }
    const created = await response.json();
    showModal.value = false;

    if (activeTab.value === "templates") {
      router.push(`/admin/templates/${created.id}`);
    } else {
      router.push(`/admin/events/${created.id}/config`);
    }
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}

onMounted(() => {
  fetchTemplates();
  fetchEvents();
});
</script>

<template>
  <div class="admin-home">
    <nav class="tabs">
      <button
        :class="['tab', { active: activeTab === 'templates' }]"
        @click="activeTab = 'templates'"
      >
        Templates
      </button>
      <button
        :class="['tab', { active: activeTab === 'events' }]"
        @click="activeTab = 'events'"
      >
        Événements
      </button>
    </nav>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- Templates tab -->
    <section v-if="activeTab === 'templates'">
      <ul v-if="templates.length" class="list">
        <li
          v-for="tpl in templates"
          :key="tpl.id"
          class="list-item"
          @click="router.push(`/admin/templates/${tpl.id}`)"
        >
          {{ tpl.name }}
        </li>
      </ul>
      <p v-else class="empty">Aucun template</p>
      <button class="btn-create" @click="showModal = true">
        + Nouveau template
      </button>
    </section>

    <!-- Events tab -->
    <section v-if="activeTab === 'events'">
      <ul v-if="events.length" class="list">
        <li
          v-for="evt in events"
          :key="evt.id"
          class="list-item"
          @click="router.push(`/admin/events/${evt.id}/config`)"
        >
          <span class="event-name">{{ evt.name }}</span>
          <span v-if="evt.date" class="event-date">{{ evt.date }}</span>
        </li>
      </ul>
      <p v-else class="empty">Aucun événement</p>
      <button class="btn-create" @click="showModal = true">
        + Nouvel événement
      </button>
    </section>

    <CreateModal
      :visible="showModal"
      :title="activeTab === 'templates' ? 'Nouveau template' : 'Nouvel événement'"
      @confirm="handleCreate"
      @cancel="showModal = false"
    />
  </div>
</template>

<style scoped>
.admin-home {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: #666;
}

.tab.active {
  color: #1976d2;
  border-bottom-color: #1976d2;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
}

.list-item {
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item:hover {
  background: #f5f5f5;
}

.event-date {
  font-size: 0.875rem;
  color: #888;
}

.empty {
  color: #888;
  font-style: italic;
  margin-bottom: 1rem;
}

.error {
  color: #d32f2f;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.btn-create {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: #1976d2;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-create:hover {
  background-color: #1565c0;
}
</style>

