import { create } from 'zustand';
import { EnrichedAlert } from '../types';
import client from '../api/client';

interface LogStore {
  logs: EnrichedAlert[];
  currentLog: EnrichedAlert | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  submitLog: (rawLog: string, source?: string) => Promise<void>;
  clearCurrentLog: () => void;
  addLogToHistory: (log: EnrichedAlert) => void;
}

export const useLogStore = create<LogStore>((set, get) => ({
  logs: [],
  currentLog: null,
  isLoading: false,
  error: null,

  submitLog: async (rawLog: string, source: string = 'unknown') => {
    set({ isLoading: true, error: null, currentLog: null });
    try {
      // Call the Orchestrator
      const response = await client.post<EnrichedAlert>('/enrich_log', {
        raw_log: rawLog,
        source: source,
        event_type: 'manual_submission',
        metadata: {}
      });

      const enrichedLog = response.data;
      
      set((state) => ({
        currentLog: enrichedLog,
        logs: [enrichedLog, ...state.logs],
        isLoading: false
      }));
    } catch (err: any) {
      console.error("Enrichment failed", err);
      set({ 
        isLoading: false, 
        error: err.response?.data?.detail || err.message || "Failed to process log" 
      });
    }
  },

  clearCurrentLog: () => set({ currentLog: null }),
  
  addLogToHistory: (log) => set((state) => ({ logs: [log, ...state.logs] }))
}));
