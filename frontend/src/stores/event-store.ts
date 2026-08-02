import { defineStore } from "pinia";
import { ref } from "vue";
import type { Course, TimeGates } from "../types/event";
import type { TrackingCompetitor } from "../types/competitor";
import { buildCompetitorBeacons, computeCurrentPh } from "../utils/competitor-state";
import { apiFetch } from "../utils/api";

export const useEventStore = defineStore("event", () => {
  const currentEventId = ref<string | null>(null);
  const name = ref("");
  const courses = ref<Course[]>([]);
  const timeGates = ref<TimeGates[]>([]);
  const competitors = ref<TrackingCompetitor[]>([]);
  const loading = ref(false);

  function findCompetitor(userId: string): TrackingCompetitor | undefined {
    return competitors.value.find((c) => c.user_id === userId);
  }

  async function fetchTracking(eventId: string, force = false): Promise<boolean> {
    if (!force && currentEventId.value === eventId && competitors.value.length > 0) {
      return true;
    }

    if (competitors.value.length === 0) {
      loading.value = true;
    }

    try {
      const res = await apiFetch(`/api/events/${eventId}/tracking`);

      if (res.status === 401) return false;
      if (!res.ok) return true;

      const data = await res.json();
      currentEventId.value = eventId;
      name.value = data.name;
      courses.value = data.courses || [];
      timeGates.value = data.time_gates || [];

      const list: TrackingCompetitor[] = [];
      for (const c of data.competitors) {
        const checkpointMap = new Map<number, { code: string | null; passage_time: string | null }>();
        for (const cp of c.checkpoints) {
          checkpointMap.set(cp.sequence, { code: cp.code, passage_time: cp.passage_time });
        }
        const phArrivals = new Map<number, string>();
        if (c.ph_arrivals) {
          for (const [key, val] of Object.entries(c.ph_arrivals)) {
            phArrivals.set(Number(key), val as string);
          }
        }
        const competitorBeacons = buildCompetitorBeacons(c.course_number, courses.value, checkpointMap, phArrivals);
        const currentPh = computeCurrentPh(competitorBeacons, c.departed, c.dns, c.abandoned);

        list.push({
          user_id: c.user_id,
          first_name: c.first_name,
          last_name: c.last_name,
          sex: c.sex || "",
          phone: c.phone || "",
          course_number: c.course_number,
          start_order: c.start_order,
          start_time_planned: c.start_time_planned,
          tracker_number: c.tracker_number,
          departed: c.departed,
          departure_time: c.departure_time,
          dns: c.dns,
          abandoned: c.abandoned,
          tracker_returned: c.tracker_returned,
          bag_weight_start: c.bag_weight_start ?? null,
          current_ph: currentPh,
          beacons: competitorBeacons,
          logs: c.logs,
        });
      }
      competitors.value = list;
      return true;
    } catch (err) {
      console.error("Failed to fetch tracking data:", err);
      return true;
    } finally {
      loading.value = false;
    }
  }

  async function fetchEventName(eventId: string, force = false): Promise<boolean> {
    if (!force && currentEventId.value === eventId && name.value) {
      return true;
    }

    try {
      const res = await apiFetch(`/api/events/${eventId}`);

      if (res.status === 401) return false;

      if (res.ok) {
        const data = await res.json();
        currentEventId.value = eventId;
        name.value = data.name;
      }
      return true;
    } catch {
      return true;
    }
  }

  function reset(): void {
    currentEventId.value = null;
    name.value = "";
    courses.value = [];
    timeGates.value = [];
    competitors.value = [];
    loading.value = false;
  }

  return {
    currentEventId,
    name,
    courses,
    timeGates,
    competitors,
    loading,
    findCompetitor,
    fetchTracking,
    fetchEventName,
    reset,
  };
});


