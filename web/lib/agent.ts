export type EnergyLevel = "low" | "medium" | "high";

export interface GoalInput {
  goal_text: string;
  available_minutes: number;
  energy_level: EnergyLevel;
  strategy_id?: string;
}

export interface FocusBlock {
  order: number;
  duration_min: number;
  task: string;
  nudge: string;
  completed?: boolean; // Added for UI state
}

export interface EvaluationScore {
  score: number;
  reasoning: string;
}

export interface PlanEvaluation {
  task_clarity: EvaluationScore;
  workload_realism: EvaluationScore;
  goal_alignment: EvaluationScore;
  motivation_quality: EvaluationScore;
  overall_score: number;
}

export interface FocusPlan {
  strategy_id: string;
  prompt_version: string;
  blocks: FocusBlock[];
  total_minutes: number;
  evaluation?: PlanEvaluation;
}

const AGENT_API_URL = "http://localhost:8000";

export async function generatePlan(input: GoalInput): Promise<FocusPlan> {
  const response = await fetch(`${AGENT_API_URL}/agent/plan?evaluate=true`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate plan");
  }

  return response.json();
}
