//! Result aggregation and statistics.

use crate::models::{
    DimensionWinner, ExperimentResult, PlanEvaluation, ScoreStats, StrategyStats, TrialResult,
};
use chrono::Utc;
use std::collections::HashMap;

/// Calculate statistics for a set of scores.
pub fn calculate_stats(scores: &[f64]) -> ScoreStats {
    if scores.is_empty() {
        return ScoreStats::default();
    }

    let count = scores.len();
    let sum: f64 = scores.iter().sum();
    let mean = sum / count as f64;

    let variance: f64 = scores.iter().map(|s| (s - mean).powi(2)).sum::<f64>() / count as f64;
    let std_dev = variance.sqrt();

    let min = scores.iter().cloned().fold(f64::INFINITY, f64::min);
    let max = scores.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

    ScoreStats {
        mean: (mean * 100.0).round() / 100.0,
        std_dev: (std_dev * 100.0).round() / 100.0,
        min,
        max,
        count,
    }
}

/// Aggregate trial results by strategy.
pub fn aggregate_by_strategy(trials: &[TrialResult]) -> Vec<StrategyStats> {
    // Group trials by strategy
    let mut by_strategy: HashMap<String, Vec<&TrialResult>> = HashMap::new();
    for trial in trials {
        by_strategy
            .entry(trial.strategy_id.clone())
            .or_default()
            .push(trial);
    }

    // Calculate stats for each strategy
    let mut stats: Vec<StrategyStats> = by_strategy
        .into_iter()
        .map(|(strategy_id, trials)| {
            let succeeded: Vec<_> = trials.iter().filter(|t| t.success).collect();
            let evaluations: Vec<&PlanEvaluation> = succeeded
                .iter()
                .filter_map(|t| t.plan.as_ref()?.evaluation.as_ref())
                .collect();

            let task_clarity: Vec<f64> = evaluations
                .iter()
                .map(|e| e.task_clarity.score as f64)
                .collect();
            let workload_realism: Vec<f64> = evaluations
                .iter()
                .map(|e| e.workload_realism.score as f64)
                .collect();
            let goal_alignment: Vec<f64> = evaluations
                .iter()
                .map(|e| e.goal_alignment.score as f64)
                .collect();
            let motivation_quality: Vec<f64> = evaluations
                .iter()
                .map(|e| e.motivation_quality.score as f64)
                .collect();
            let overall: Vec<f64> = evaluations.iter().map(|e| e.overall_score).collect();

            let durations: Vec<f64> = trials.iter().map(|t| t.duration_ms as f64).collect();
            let avg_duration = if durations.is_empty() {
                0.0
            } else {
                durations.iter().sum::<f64>() / durations.len() as f64
            };

            StrategyStats {
                strategy_id,
                trials_run: trials.len(),
                trials_succeeded: succeeded.len(),
                task_clarity: calculate_stats(&task_clarity),
                workload_realism: calculate_stats(&workload_realism),
                goal_alignment: calculate_stats(&goal_alignment),
                motivation_quality: calculate_stats(&motivation_quality),
                overall: calculate_stats(&overall),
                avg_duration_ms: (avg_duration * 100.0).round() / 100.0,
            }
        })
        .collect();

    // Sort by strategy_id for consistent output
    stats.sort_by(|a, b| a.strategy_id.cmp(&b.strategy_id));
    stats
}

/// Find the best strategy for each dimension.
pub fn find_dimension_winners(stats: &[StrategyStats]) -> Vec<DimensionWinner> {
    if stats.is_empty() {
        return vec![];
    }

    fn find_winner(
        stats: &[StrategyStats],
        dimension: &str,
        getter: fn(&StrategyStats) -> f64,
    ) -> DimensionWinner {
        let winner = stats
            .iter()
            .max_by(|a, b| getter(a).partial_cmp(&getter(b)).unwrap())
            .unwrap();
        DimensionWinner {
            dimension: dimension.to_string(),
            winner: winner.strategy_id.clone(),
            score: getter(winner),
        }
    }

    vec![
        find_winner(stats, "task_clarity", |s| s.task_clarity.mean),
        find_winner(stats, "workload_realism", |s| s.workload_realism.mean),
        find_winner(stats, "goal_alignment", |s| s.goal_alignment.mean),
        find_winner(stats, "motivation_quality", |s| s.motivation_quality.mean),
        find_winner(stats, "overall", |s| s.overall.mean),
    ]
}

/// Build the complete experiment result.
pub fn build_experiment_result(
    experiment_name: &str,
    num_goals: usize,
    trials: Vec<TrialResult>,
) -> ExperimentResult {
    let strategy_stats = aggregate_by_strategy(&trials);
    let dimension_winners = find_dimension_winners(&strategy_stats);

    // Get prompt version from first successful trial
    let prompt_version = trials
        .iter()
        .find_map(|t| t.plan.as_ref().map(|p| p.prompt_version.clone()))
        .unwrap_or_else(|| "unknown".to_string());

    // Get strategies tested
    let mut strategies_tested: Vec<String> =
        strategy_stats.iter().map(|s| s.strategy_id.clone()).collect();
    strategies_tested.sort();

    // Find best overall strategy
    let best_overall = dimension_winners
        .iter()
        .find(|w| w.dimension == "overall")
        .map(|w| w.winner.clone())
        .unwrap_or_else(|| "unknown".to_string());

    ExperimentResult {
        experiment_name: experiment_name.to_string(),
        timestamp: Utc::now().to_rfc3339(),
        prompt_version,
        num_goals,
        strategies_tested,
        trials,
        strategy_stats,
        best_overall,
        dimension_winners,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_stats_empty() {
        let stats = calculate_stats(&[]);
        assert_eq!(stats.count, 0);
        assert_eq!(stats.mean, 0.0);
    }

    #[test]
    fn test_calculate_stats() {
        let scores = vec![7.0, 8.0, 9.0, 8.0, 8.0];
        let stats = calculate_stats(&scores);
        assert_eq!(stats.count, 5);
        assert_eq!(stats.mean, 8.0);
        assert_eq!(stats.min, 7.0);
        assert_eq!(stats.max, 9.0);
    }
}
