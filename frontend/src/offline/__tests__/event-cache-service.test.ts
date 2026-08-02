import { describe, it, expect, beforeEach } from "vitest";

import "fake-indexeddb/auto";

import { eventCacheService } from "../../offline/event-cache-service";
import { db } from "../../offline/db";

describe("EventCacheService", () => {
  beforeEach(async () => {
    await db.eventCache.clear();
    await db.eventListCache.clear();
  });

  describe("saveTracking / getTracking", () => {
    it("saves and retrieves tracking data for an event", async () => {
      const data = { name: "Test", courses: [{ number: 1 }], competitors: [] };
      await eventCacheService.saveTracking("evt-1", data);

      const result = await eventCacheService.getTracking("evt-1");
      expect(result).toEqual(data);
    });

    it("returns null for unknown event", async () => {
      const result = await eventCacheService.getTracking("unknown");
      expect(result).toBeNull();
    });

    it("overwrites existing cache", async () => {
      await eventCacheService.saveTracking("evt-1", { name: "Old" });
      await eventCacheService.saveTracking("evt-1", { name: "New" });

      const result = await eventCacheService.getTracking("evt-1");
      expect((result as any).name).toBe("New");
    });
  });

  describe("saveEventList / getEventList", () => {
    it("saves and retrieves event list", async () => {
      const list = [{ id: "1", name: "A" }, { id: "2", name: "B" }];
      await eventCacheService.saveEventList(list);

      const result = await eventCacheService.getEventList();
      expect(result).toEqual(list);
    });

    it("returns null when no list cached", async () => {
      const result = await eventCacheService.getEventList();
      expect(result).toBeNull();
    });
  });

  describe("clear", () => {
    it("removes all cached data", async () => {
      await eventCacheService.saveTracking("evt-1", { name: "Test" });
      await eventCacheService.saveEventList([{ id: "1" }]);

      await eventCacheService.clear();

      expect(await eventCacheService.getTracking("evt-1")).toBeNull();
      expect(await eventCacheService.getEventList()).toBeNull();
    });
  });
});

