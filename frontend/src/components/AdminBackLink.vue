<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  to: string;
}>();

const isOrganizer = computed(() => {
  const token = localStorage.getItem("token");
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (payload.exp && Date.now() >= payload.exp * 1000) return false;
    return payload.role === "organizer";
  } catch {
    return false;
  }
});
</script>

<template>
  <router-link v-if="isOrganizer" :to="props.to" class="admin-back-link">
    ← Vue encadrant
  </router-link>
</template>

<style scoped>
.admin-back-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.8rem;
  position: absolute;
  top: 0.5rem;
  right: 0.75rem;
}

.admin-back-link:hover {
  color: #fff;
  text-decoration: underline;
}
</style>

