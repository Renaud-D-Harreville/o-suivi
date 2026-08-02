<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";

const props = defineProps<{
  eventId: string;
  eventName: string;
}>();

const router = useRouter();
const route = useRoute();

const navItems = [
  { key: "config", label: "Config", routeName: "event-config" },
  { key: "depart", label: "Départ", routeName: "event-depart" },
  { key: "suivi", label: "Suivi", routeName: "event-suivi" },
  { key: "resultats", label: "Résultats", routeName: "event-resultats" },
] as const;

function isActive(routeName: string): boolean {
  return route.name === routeName;
}

function navigate(routeName: string) {
  router.push({ name: routeName, params: { id: props.eventId } });
}
</script>

<template>
  <header class="event-header">
    <div class="header-top">
      <button class="back-btn" @click="router.push('/admin')">← Retour</button>
      <h1>{{ eventName || "Événement" }}</h1>
    </div>
    <nav class="header-nav">
      <button
        v-for="item in navItems"
        :key="item.key"
        :class="['nav-btn', { active: isActive(item.routeName) }]"
        @click="navigate(item.routeName)"
      >
        {{ item.label }}
      </button>
    </nav>
  </header>
</template>

<style scoped>
.event-header {
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 100;
  border-bottom: 1px solid #e0e0e0;
  padding: 0.75rem 1rem 0;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
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
  font-size: 1.25rem;
  margin: 0;
}

.header-nav {
  display: flex;
  gap: 0;
}

.nav-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: #666;
  white-space: nowrap;
}

.nav-btn.active {
  color: #1976d2;
  border-bottom-color: #1976d2;
}

.nav-btn:hover:not(.active) {
  color: #333;
}
</style>

