import Dexie, { type Table } from "dexie";
import type { PendingAction } from "./pending-action";

export interface EventCacheEntry {
  eventId: string;
  data: unknown;
  updatedAt: string;
}

export interface ListCacheEntry {
  key: string;
  data: unknown;
  updatedAt: string;
}

export class OfflineDatabase extends Dexie {
  pendingActions!: Table<PendingAction, number>;
  eventCache!: Table<EventCacheEntry, string>;
  eventListCache!: Table<ListCacheEntry, string>;

  constructor() {
    super("o-suivi-offline");
    this.version(1).stores({
      pendingActions: "++id, createdAt, failed",
      eventCache: "eventId",
      eventListCache: "key",
    });
  }
}

export const db = new OfflineDatabase();


