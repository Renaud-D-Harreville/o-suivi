import { ref, type Ref } from "vue";
import type { TrackingCompetitor } from "../types/competitor";
import { toLocalISO } from "../utils/date";
import { computeCurrentPh } from "../utils/competitor-state";
import { apiFetch } from "../utils/api";
import { usePrompt } from "./usePrompt";

export function useCompetitorActions(
  eventId: string,
  competitors: Ref<TrackingCompetitor[]>,
) {
  const pending = ref(false);
  const { prompt } = usePrompt();

  async function markAbandon(userId: string): Promise<void> {
    const comment = await prompt("Raison de l'abandon", { placeholder: "Ex: fatigue, blessure..." });
    if (!comment) return;

    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/abandon`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, comment }),
        },
      );
      if (res.ok) {
        const comp = competitors.value.find((c) => c.user_id === userId);
        if (comp) {
          comp.abandoned = true;
          comp.current_ph = null;
        }
      }
    } finally {
      pending.value = false;
    }
  }

  async function cancelAbandon(userId: string): Promise<void> {
    const comment = await prompt("Raison de l'annulation", { placeholder: "Ex: erreur de saisie..." });
    if (!comment) return;

    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/abandon-cancel`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, comment }),
        },
      );
      if (res.ok) {
        const comp = competitors.value.find((c) => c.user_id === userId);
        if (comp) {
          comp.abandoned = false;
          comp.current_ph = computeCurrentPh(comp.beacons, comp.departed, comp.dns, false);
        }
      }
    } finally {
      pending.value = false;
    }
  }

  async function markTrackerReturned(userId: string): Promise<void> {
    const comp = competitors.value.find((c) => c.user_id === userId);
    const trackerNumber = await prompt(
      `N° du tracker rendu${comp?.tracker_number ? ` (prêté : ${comp.tracker_number})` : ""}`,
      { placeholder: "Ex: 42", defaultValue: comp?.tracker_number || "" },
    );
    if (!trackerNumber) return;

    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/tracker-returned`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date, tracker_number: trackerNumber }),
        },
      );
      if (res.ok && comp) {
        comp.tracker_returned = true;
      }
    } finally {
      pending.value = false;
    }
  }

  async function cancelTrackerReturned(userId: string): Promise<void> {
    pending.value = true;
    try {
      const creation_date = toLocalISO(new Date());
      const res = await apiFetch(
        `/api/events/${eventId}/registrations/${userId}/tracker-returned-cancel`,
        {
          method: "POST",
          body: JSON.stringify({ creation_date }),
        },
      );
      if (res.ok) {
        const comp = competitors.value.find((c) => c.user_id === userId);
        if (comp) comp.tracker_returned = false;
      }
    } finally {
      pending.value = false;
    }
  }

  return { pending, markAbandon, cancelAbandon, markTrackerReturned, cancelTrackerReturned };
}

