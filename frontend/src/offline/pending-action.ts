export interface PendingAction {
  id?: number;
  url: string;
  method: string;
  body: string | null;
  createdAt: string;
  retryCount: number;
  failed: boolean;
}

