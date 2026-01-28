//! Data models for FocusOS experiments.
//!
//! These models mirror the Python API types for seamless JSON serialization.

use serde::{Deserialize, Serialize};

/// Energy level for a focus session.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum EnergyLevel {
    Low,
    Medium,
    High,
}

impl std::fmt::Display for EnergyLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EnergyLevel::Low => write!(f, "low"),
            EnergyLevel::Medium => write!(f, "medium"),
            EnergyLevel::High => write!(f, "high"),
        }
    }
}

/// A test goal for experimentation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperimentGoal {
    /// Unique identifier for the goal
    pub id: String,
    /// The goal text to plan for
    pub goal_text: String,
    /// Available time in minutes
    pub available_minutes: u32,
    /// Energy level
    pub energy_level: EnergyLevel,
    /// Category for analysis (e.g., "technical", "creative", "admin")
    pub category: String,
}

/// Request body for the /agent/plan endpoint.
#[derive(Debug, Clone, Serialize)]
pub struct PlanRequest {
    pub goal_text: String,
    pub available_minutes: u32,
    pub energy_level: EnergyLevel,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub strategy_id: Option<String>,
}

impl From<&ExperimentGoal> for PlanRequest {
    fn from(goal: &ExperimentGoal) -> Self {
        Self {
            goal_text: goal.goal_text.clone(),
            available_minutes: goal.available_minutes,
            energy_level: goal.energy_level,
            strategy_id: None,
        }
    }
}

/// A single focus block in a plan.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FocusBlock {
    pub order: u32,
    pub duration_min: u32,
    pub task: String,
    pub nudge: String,
}

/// Evaluation score for a single dimension.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationScore {
    pub score: u32,
    pub reasoning: String,
}

/// Complete plan evaluation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlanEvaluation {
    pub task_clarity: EvaluationScore,
    pub workload_realism: EvaluationScore,
    pub goal_alignment: EvaluationScore,
    pub motivation_quality: EvaluationScore,
    pub overall_score: f64,
}

/// Response from the /agent/plan endpoint.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlanResponse {
    pub strategy_id: String,
    pub prompt_version: String,
    pub blocks: Vec<FocusBlock>,
    pub total_minutes: u32,
    pub evaluation: Option<PlanEvaluation>,
}

/// Strategy information from /strategies endpoint.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Strategy {
    pub id: String,
    pub description: String,
    pub tone: String,
    pub block_length_min: u32,
    pub density: String,
}

/// Response from /strategies endpoint.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategiesResponse {
    pub strategies: Vec<Strategy>,
}

/// Result of a single trial (one goal + one strategy).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrialResult {
    pub goal_id: String,
    pub strategy_id: String,
    pub success: bool,
    pub plan: Option<PlanResponse>,
    pub error: Option<String>,
    pub duration_ms: u64,
}

/// Aggregated statistics for a set of scores.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoreStats {
    pub mean: f64,
    pub std_dev: f64,
    pub min: f64,
    pub max: f64,
    pub count: usize,
}

impl Default for ScoreStats {
    fn default() -> Self {
        Self {
            mean: 0.0,
            std_dev: 0.0,
            min: 0.0,
            max: 0.0,
            count: 0,
        }
    }
}

/// Aggregated results for a single strategy.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategyStats {
    pub strategy_id: String,
    pub trials_run: usize,
    pub trials_succeeded: usize,
    pub task_clarity: ScoreStats,
    pub workload_realism: ScoreStats,
    pub goal_alignment: ScoreStats,
    pub motivation_quality: ScoreStats,
    pub overall: ScoreStats,
    pub avg_duration_ms: f64,
}

/// Comparison of strategies by dimension.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DimensionWinner {
    pub dimension: String,
    pub winner: String,
    pub score: f64,
}

/// Complete experiment results.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperimentResult {
    pub experiment_name: String,
    pub timestamp: String,
    pub prompt_version: String,
    pub num_goals: usize,
    pub strategies_tested: Vec<String>,
    pub trials: Vec<TrialResult>,
    pub strategy_stats: Vec<StrategyStats>,
    pub best_overall: String,
    pub dimension_winners: Vec<DimensionWinner>,
}
