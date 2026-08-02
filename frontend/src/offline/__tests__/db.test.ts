import { describe, it, expect, beforeEach, vi } from "vitest";

// Mock IndexedDB via fake-indexeddb for Dexie
import "fake-indexeddb/auto";

import { db } from "../../offline/db";
import type { PendingAction } from "../../offline/pending-action";

describe("OfflineDatabase", () => {
  beforeEach(async () => {
    await db.pendingActions.clear();
    await db.eventCache.clear();
    await db.eventListCache.clear();
  });

  describe("pendingActions table", () => {
    it("stores and retrieves a pending action", async () => {
      const action: PendingAction = {
        url: "/api/events/abc/registrations/u1/depart",
        method: "POST",
        body: JSON.stringify({ creation_date: "2026-08-03T10:00:00Z" }),
        createdAt: "2026-08-03T10:00:00.000Z",
        retryCount: 0,
        failed: false,
      };

      const id = await db.pendingActions.add(action);
      expect(id).toBeGreaterThan(0);

      const stored = await db.pendingActions.get(id);
      expect(stored).toBeDefined();
      expect(stored!.url).toBe(action.url);
      expect(stored!.method).toBe("POST");
      expect(stored!.retryCount).toBe(0);
      expect(stored!.failed).toBe(false);
    });

    it("returns actions sorted by createdAt", async () => {
      await db.pendingActions.add({
        url: "/api/a",
        method: "POST",
        body: null,
        createdAt: "2026-08-03T10:02:00.000Z",
        retryCount: 0,
        failed: false,
      });
      await db.pendingActions.add({
        url: "/api/b",
        method: "POST",
        body: null,
        createdAt: "2026-08-03T10:01:00.000Z",
        retryCount: 0,
        failed: false,
      });

      const sorted = await db.pendingActions.orderBy("createdAt").toArray();
      expect(sorted[0].url).toBe("/api/b");
      expect(sorted[1].url).toBe("/api/a");
    });

    it("deletes a pending action by id", async () => {
      const id = await db.pendingActions.add({
        url: "/api/x",
        method: "DELETE",
        body: null,
        createdAt: "2026-08-03T10:00:00.000Z",
        retryCount: 0,
        failed: false,
      });

      await db.pendingActions.delete(id);
      const result = await db.pendingActions.get(id);
      expect(result).toBeUndefined();
    });
  });

  describe("eventCache table", () => {
    it("stores and retrieves event cache data", async () => {
      const data = { name: "Test Event", courses: [], competitors: [] };
      await db.eventCache.put({
        eventId: "evt-1",
        data,
        updatedAt: "2026-08-03T10:00:00.000Z",
      });

      const result = await db.eventCache.get("evt-1");
      expect(result).toBeDefined();
      expect(result!.data).toEqual(data);
    });

    it("overwrites cache on put with same eventId", async () => {
      await db.eventCache.put({
        eventId: "evt-1",
        data: { name: "Old" },
        updatedAt: "2026-08-03T09:00:00.000Z",
      });
      await db.eventCache.put({
        eventId: "evt-1",
        data: { name: "New" },
        updatedAt: "2026-08-03T10:00:00.000Z",
      });

      const result = await db.eventCache.get("evt-1");
      expect((result!.data as any).name).toBe("New");
    });
  });

  describe("eventListCache table", () => {
    it("stores and retrieves event list", async () => {
      const list = [{ id: "1", name: "Event A" }];
      await db.eventListCache.put({
        key: "list",
        data: list,
        updatedAt: "2026-08-03T10:00:00.000Z",
      });

      const result = await db.eventListCache.get("list");
      expect(result!.data).toEqual(list);
    });
  });
});

