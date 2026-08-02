import { ref, onMounted, onUnmounted } from "vue";

export function useClock() {
  const currentTime = ref(new Date());
  let intervalId: number | undefined;

  onMounted(() => {
    intervalId = window.setInterval(() => {
      currentTime.value = new Date();
    }, 1000);
  });

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
  });

  return { currentTime };
}

