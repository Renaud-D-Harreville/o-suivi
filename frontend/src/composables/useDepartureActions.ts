import { ref, type Ref } from "vue";
import type { TrackingCompetitor } from "../types/competitor";
import { toLocalISO } from "../utils/date";
import { apiFetch } from "../utils/api";
import { usePrompt } from "./usePrompt";
import { useEventStore } from "../stores/event-store";

export function useDepartureActions(
  eventId: string,
  _competitors: Ref<TrackingCompetitor[]>,
) {
  const pending = ref(false);
  const store = useEventStore();
  const { prompt } = usePrompt();

  async function refreshData(): Promise<void> {
    await store.fetchTracking(eventId, true);
  }

  async function confirmDeparture(userId: string): Promise<void> {
    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/depart`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date }),
        },
      );
      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  async function confirmDepartureWithTime(userId: string, timeValue: string): Promise<void> {
    if (!timeValue) return;
    pending.value = true;
    try {
      const today = new Date();
      const [hours, minutes] = timeValue.split(":").map(Number);
      today.setHours(hours, minutes, 0, 0);
      const departure_time = toLocalISO(today);
      const creation_date = toLocalISO(new Date());

      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/depart-edit`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, departure_time }),
        },
      );
      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  async function cancelDeparture(userId: string): Promise<void> {
    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/depart-cancel`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date }),
        },
      );
      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  async function markDns(userId: string): Promise<void> {
    const comment = await prompt("Raison de l'absence", { placeholder: "Ex: non présenté..." });
    if (!comment) return;

    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/dns`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, comment }),
        },
      );
      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  async function cancelDns(userId: string): Promise<void> {
    const comment = await prompt("Raison de l'annulation", { placeholder: "Ex: erreur de saisie..." });
    if (!comment) return;

    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/dns-cancel`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, comment }),
        },
      );
      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  async function saveRegistrationField(
    userId: string,
    field: string,
    value: string | null,
  ): Promise<void> {
    pending.value = true;
    try {
      const payload: Record<string, unknown> = {};

      if (field === "start_time_planned") {
        payload.start_time_planned = value;
      } else if (field === "course_number") {
        payload.course_number = value ? parseInt(value) : null;
      } else if (field === "tracker_number") {
        payload.tracker_number = value;
      } else if (field === "bag_weight") {
        if (value) {
          const creation_date = toLocalISO(new Date());
          const res = await apiFetch(
            `/api/events/${eventId}/registrations/${userId}/bag-weight`,
            {
              method: "POST",
              body: JSON.stringify({ creation_date, moment: "start", weight_kg: parseFloat(value) }),
            },
          );
          if (res.ok) {
            await refreshData();
          }
        }
        return;
      }

      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}`,
        {
          method: "PATCH",
          body: JSON.stringify(payload),
        },
      );

      if (res.ok) {
        await refreshData();
      }
    } finally {
      pending.value = false;
    }
  }

  return {
    pending,
    confirmDeparture,
    confirmDepartureWithTime,
    cancelDeparture,
    markDns,
    cancelDns,
    saveRegistrationField,
  };
}

