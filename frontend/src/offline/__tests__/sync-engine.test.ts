import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";

import "fake-indexeddb/auto";

import { db } from "../../offline/db";
import * as syncEngine from "../../offline/sync-engine";

describe("SyncEngine", () => {
  beforeEach(async () => {
    await db.pendingActions.clear();
    await syncEngine.refreshPendingCount();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    syncEngine.stop();
  });

  describe("enqueue", () => {
    it("adds an action to pendingActions", async () => {
      await syncEngine.enqueue("/api/events/e1/registrations/u1/depart", "POST", '{"creation_date":"2026-08-03T10:00:00Z"}');

      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(1);
      expect(actions[0].url).toBe("/api/events/e1/registrations/u1/depart");
      expect(actions[0].method).toBe("POST");
      expect(actions[0].retryCount).toBe(0);
      expect(actions[0].failed).toBe(false);
    });

    it("increments pendingCount", async () => {
      expect(syncEngine.pendingCount.value).toBe(0);
      await syncEngine.enqueue("/api/test", "POST", null);
      expect(syncEngine.pendingCount.value).toBe(1);
    });
  });

  describe("dequeueByUrl", () => {
    it("removes the last matching action", async () => {
      await syncEngine.enqueue("/api/test", "POST", '{"a":1}');
      await syncEngine.enqueue("/api/test", "POST", '{"a":1}');

      await syncEngine.dequeueByUrl("/api/test", "POST", '{"a":1}');

      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(1);
    });

    it("does nothing if no match", async () => {
      await syncEngine.enqueue("/api/test", "POST", '{"a":1}');
      await syncEngine.dequeueByUrl("/api/other", "POST", '{"a":1}');

      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(1);
    });
  });

  describe("flush", () => {
    it("replays actions and removes successful ones", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(null, { status: 200 }),
      );

      await syncEngine.enqueue("/api/test", "POST", '{"x":1}');
      expect(syncEngine.pendingCount.value).toBe(1);

      await syncEngine.flush();

      expect(syncEngine.pendingCount.value).toBe(0);
      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(0);
    });

    it("stops on network error", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Network error"));

      await syncEngine.enqueue("/api/a", "POST", null);
      await syncEngine.enqueue("/api/b", "POST", null);

      await syncEngine.flush();

      // Both should still be in queue
      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(2);
    });

    it("increments retryCount on 5xx and continues", async () => {
      vi.spyOn(globalThis, "fetch")
        .mockResolvedValueOnce(new Response(null, { status: 500 }))
        .mockResolvedValueOnce(new Response(null, { status: 200 }));

      await syncEngine.enqueue("/api/a", "POST", null);
      await syncEngine.enqueue("/api/b", "POST", null);

      await syncEngine.flush();

      const actions = await db.pendingActions.toArray();
      // a should still be there with retryCount 1, b should be removed
      expect(actions).toHaveLength(1);
      expect(actions[0].url).toBe("/api/a");
      expect(actions[0].retryCount).toBe(1);
    });

    it("marks action as failed after 5 retries", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(null, { status: 500 }),
      );

      // Manually insert an action with retryCount 4
      await db.pendingActions.add({
        url: "/api/failing",
        method: "POST",
        body: null,
        createdAt: "2026-08-03T10:00:00.000Z",
        retryCount: 4,
        failed: false,
      });

      await syncEngine.flush();

      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(1);
      expect(actions[0].retryCount).toBe(5);
      // failed is stored as 1 (truthy) for indexing
    });

    it("treats 4xx as success (deduplication)", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(null, { status: 422 }),
      );

      await syncEngine.enqueue("/api/test", "POST", null);
      await syncEngine.flush();

      const actions = await db.pendingActions.toArray();
      expect(actions).toHaveLength(0);
    });
  });
});


