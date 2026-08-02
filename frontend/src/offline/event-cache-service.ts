import { db, type EventCacheEntry } from "./db";

export class EventCacheService {
  async saveTracking(eventId: string, data: unknown): Promise<void> {
    const entry: EventCacheEntry = {
      eventId,
      data,
      updatedAt: new Date().toISOString(),
    };
    await db.eventCache.put(entry);
  }

  async getTracking(eventId: string): Promise<unknown | null> {
    const entry = await db.eventCache.get(eventId);
    return entry?.data ?? null;
  }

  async saveEventList(data: unknown): Promise<void> {
    await db.eventListCache.put({
      key: "list",
      data,
      updatedAt: new Date().toISOString(),
    });
  }

  async getEventList(): Promise<unknown | null> {
    const entry = await db.eventListCache.get("list");
    return entry?.data ?? null;
  }

  async clear(): Promise<void> {
    await db.eventCache.clear();
    await db.eventListCache.clear();
  }
}

export const eventCacheService = new EventCacheService();

