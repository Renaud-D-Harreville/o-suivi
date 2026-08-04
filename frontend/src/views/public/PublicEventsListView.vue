<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import type { EventSummary } from "../../types/results";
import AdminBackLink from "../../components/AdminBackLink.vue";

const events = ref<EventSummary[]>([]);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const resp = await fetch("/api/events");
    if (!resp.ok) {
      error.value = "Impossible de charger les événements";
      return;
    }
    events.value = await resp.json();
  } catch {
    error.value = "Impossible de contacter le serveur";
  } finally {
    loading.value = false;
  }
});

const sortedEvents = computed(() => {
  return [...events.value].sort((a, b) => {
    if (!a.date && !b.date) return 0;
    if (!a.date) return 1;
    if (!b.date) return -1;
    return b.date.localeCompare(a.date);
  });
});

function formatDate(date: string | null): string {
  if (!date) return "";
  const [year, month, day] = date.split("-");
  return `${day}/${month}/${year}`;
}
</script>

<template>
  <div class="public-events">
    <div class="admin-link-wrapper">
      <AdminBackLink to="/admin" />
    </div>
    <h1>Événements publics</h1>

    <p v-if="loading" class="message">Chargement…</p>
    <p v-else-if="error" class="message error">{{ error }}</p>
    <p v-else-if="sortedEvents.length === 0" class="message">Aucun événement disponible</p>

    <ul v-else class="event-list">
      <li v-for="event in sortedEvents" :key="event.id">
        <router-link :to="`/events/${event.id}`" class="event-link">
          <span v-if="event.date" class="event-date">{{ formatDate(event.date) }}</span>
          <span class="event-name">{{ event.name }}</span>
        </router-link>
      </li>
    </ul>

    <div class="footer-link">
      <router-link to="/login">Connexion encadrant</router-link>
    </div>
  </div>
</template>

<style scoped>
.public-events {
  max-width: 480px;
  margin: 4rem auto;
  padding: 2rem;
  position: relative;
}

.admin-link-wrapper {
  position: absolute;
  top: 0.5rem;
  right: 0.75rem;
}

.admin-link-wrapper :deep(.admin-back-link) {
  color: #1976d2;
  position: static;
}

h1 {
  margin-bottom: 1.5rem;
}

.message {
  color: #666;
}

.message.error {
  color: #d32f2f;
}

.event-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.event-list li {
  margin-bottom: 0.5rem;
}

.event-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.15s;
}

.event-link:hover {
  background-color: #f5f5f5;
}

.event-date {
  color: #aaa;
  font-size: 0.875rem;
  white-space: nowrap;
}

.event-name {
  font-weight: 500;
}

.footer-link {
  margin-top: 2rem;
  text-align: center;
}

.footer-link a {
  color: #1976d2;
  text-decoration: none;
  font-size: 0.875rem;
}

.footer-link a:hover {
  text-decoration: underline;
}
</style>

