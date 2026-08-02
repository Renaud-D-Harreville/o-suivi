<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import EventHeader from "../../components/EventHeader.vue";
import GeneralTab from "./event-tabs/GeneralTab.vue";
import BeaconsTab from "./event-tabs/BeaconsTab.vue";
import CoursesTab from "./event-tabs/CoursesTab.vue";
import ParticipantsTab from "./event-tabs/ParticipantsTab.vue";
import ScheduleTab from "./event-tabs/ScheduleTab.vue";
import TimeGatesTab from "./event-tabs/TimeGatesTab.vue";
import { useEventStore } from "../../stores/event-store";

const route = useRoute();
const router = useRouter();
const eventId = route.params.id as string;

const store = useEventStore();
const { name: eventName } = storeToRefs(store);

const tabs = [
  { key: "general", label: "Général" },
  { key: "beacons", label: "Balises" },
  { key: "courses", label: "Parcours" },
  { key: "participants", label: "Participants" },
  { key: "schedule", label: "Horaires" },
  { key: "time-gates", label: "Barrières horaires" },
] as const;

type TabKey = (typeof tabs)[number]["key"];

const activeTab = ref<TabKey>("general");

async function loadEventName() {
  const ok = await store.fetchEventName(eventId);
  if (!ok) router.push("/login");
}

async function refreshEventName() {
  await store.fetchEventName(eventId, true);
}

onMounted(loadEventName);
</script>

<template>
  <div class="event-config">
    <EventHeader :event-id="eventId" :event-name="eventName" />

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
      <GeneralTab
        v-if="activeTab === 'general'"
        :event-id="eventId"
        @saved="refreshEventName"
      />
      <BeaconsTab v-else-if="activeTab === 'beacons'" :event-id="eventId" />
      <CoursesTab v-else-if="activeTab === 'courses'" :event-id="eventId" />
      <ParticipantsTab v-else-if="activeTab === 'participants'" :event-id="eventId" />
      <ScheduleTab v-else-if="activeTab === 'schedule'" :event-id="eventId" />
      <TimeGatesTab v-else-if="activeTab === 'time-gates'" :event-id="eventId" />
    </section>
  </div>
</template>

<style scoped>
.event-config {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 1rem 1rem;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
  gap: 0;
  overflow-x: auto;
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

