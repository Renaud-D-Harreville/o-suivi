<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import BeaconsTab from "./template-tabs/BeaconsTab.vue";
import CoursesTab from "./template-tabs/CoursesTab.vue";
import TimeGatesTab from "./template-tabs/TimeGatesTab.vue";
import { useAuth } from "../../composables/useAuth";

const route = useRoute();
const router = useRouter();
const templateId = route.params.id as string;
const { getAuthHeaders } = useAuth();

const tabs = [
  { key: "beacons", label: "Registre balises" },
  { key: "courses", label: "Parcours" },
  { key: "time-gates", label: "Temps PH" },
] as const;

type TabKey = (typeof tabs)[number]["key"];

const activeTab = ref<TabKey>("beacons");
const templateName = ref("");


async function fetchTemplateName() {
  try {
    const response = await fetch(`/api/templates/${templateId}`, {
      headers: getAuthHeaders(),
    });
    if (response.status === 401) {
      router.push("/login");
      return;
    }
    if (response.ok) {
      const data = await response.json();
      templateName.value = data.name;
    }
  } catch {
    /* will be handled by the tab */
  }
}

onMounted(fetchTemplateName);
</script>

<template>
  <div class="template-config">
    <header class="template-header">
      <button class="back-btn" @click="router.push('/admin')">← Retour</button>
      <h1>{{ templateName || "Template" }}</h1>
    </header>

    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </nav>

    <section class="tab-content">
      <BeaconsTab v-if="activeTab === 'beacons'" :template-id="templateId" />
      <CoursesTab v-else-if="activeTab === 'courses'" :template-id="templateId" />
      <TimeGatesTab v-else-if="activeTab === 'time-gates'" :template-id="templateId" />
    </section>
  </div>
</template>

<style scoped>
.template-config {
  max-width: 900px;
  margin: 1rem auto;
  padding: 1rem;
}

.template-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.back-btn {
  background: none;
  border: none;
  font-size: 0.875rem;
  color: #1976d2;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.back-btn:hover {
  text-decoration: underline;
}

h1 {
  font-size: 1.5rem;
  margin: 0;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
  gap: 0;
}

.tab {
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: #666;
  white-space: nowrap;
}

.tab.active {
  color: #1976d2;
  border-bottom-color: #1976d2;
}

.tab-content {
  padding: 0.5rem 0;
}
</style>

