export interface NormalizedLog {
  timestamp: string;
  source: string;
  event_type: string;
  hostname?: string;
  user?: string;
  message?: string;
  raw_log: string;
  normalized_fields: Record<string, any>;
}

export interface SemanticResult {
  semantic_summary: string;
  semantic_features: Record<string, any>;
  confidence: number;
}

export interface IntentResult {
  intent: string;
  tactic: string;
  score: number;
  matched_rules: string[];
  source: "rules" | "llm";
  explanation?: string;
}

export interface MitreResult {
  attack_technique: string;
  technique_id: string;
  tactic: string;
  kill_chain_phase: string;
  confidence: number;
  explanation: string;
  related_techniques: string[];
}

export interface RiskScore {
  score: number;
  level: "low" | "medium" | "high" | "critical";
  factors: Record<string, any>;
}

export interface EnrichedAlert {
  correlation_id: string;
  raw_log: string;
  source: string;
  event_type?: string;
  normalized?: NormalizedLog;
  semantic?: SemanticResult;
  intent?: IntentResult;
  mitre?: MitreResult;
  risk?: RiskScore;
  summary?: string;
  recommendations: string[];
  errors: string[];
}
