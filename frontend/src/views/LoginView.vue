<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const error = ref("");

async function handleLogin() {
  error.value = "";

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, password: password.value }),
    });

    if (!response.ok) {
      error.value = "Identifiants incorrects";
      return;
    }

    const data = await response.json();
    localStorage.setItem("token", data.token);
    router.push("/admin");
  } catch {
    error.value = "Impossible de contacter le serveur";
  }
}
</script>

<template>
  <div class="login">
    <h1>Connexion encadrant</h1>
    <form @submit.prevent="handleLogin">
      <div class="field">
        <label for="username">Pseudo</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          required
        />
      </div>
      <div class="field">
        <label for="password">Mot de passe</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit">Se connecter</button>
    </form>
    <div class="footer-link">
      <router-link to="/events">Événements publics</router-link>
    </div>
  </div>
</template>

<style scoped>
.login {
  max-width: 320px;
  margin: 4rem auto;
  padding: 2rem;
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

input {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.error {
  color: #d32f2f;
  font-size: 0.875rem;
}

button {
  width: 100%;
  padding: 0.625rem;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background-color: #1976d2;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #1565c0;
}

.footer-link {
  margin-top: 1.5rem;
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

