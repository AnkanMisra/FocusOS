//! Experiment runner for parallel strategy comparison.

use anyhow::{Context, Result};
use indicatif::{ProgressBar, ProgressStyle};
use std::sync::Arc;
use tokio::sync::Semaphore;

use crate::client::AgentClient;
use crate::models::{ExperimentGoal, PlanRequest, TrialResult};

/// Configuration for running experiments.
#[derive(Debug, Clone)]
pub struct ExperimentConfig {
    /// Maximum concurrent requests to the agent API
    pub max_concurrency: usize,
    /// Base URL for the agent API
    pub agent_url: String,
    /// Strategies to test (None = all available)
    pub strategies: Option<Vec<String>>,
}

impl Default for ExperimentConfig {
    fn default() -> Self {
        Self {
            max_concurrency: 3, // Conservative to avoid overwhelming the API
            agent_url: "http://localhost:8000".to_string(),
            strategies: None,
        }
    }
}

/// Run all trials for the experiment.
pub async fn run_trials(
    goals: &[ExperimentGoal],
    config: &ExperimentConfig,
) -> Result<Vec<TrialResult>> {
    let client = AgentClient::new(&config.agent_url)?;

    // Verify agent is running
    if !client.health_check().await.unwrap_or(false) {
        anyhow::bail!(
            "Agent is not responding at {}. Make sure it's running.",
            config.agent_url
        );
    }

    // Get strategies
    let strategies = match &config.strategies {
        Some(s) => s.clone(),
        None => {
            let resp = client
                .get_strategies()
                .await
                .context("Failed to fetch strategies")?;
            resp.strategies.into_iter().map(|s| s.id).collect()
        }
    };

    // Calculate total trials
    let total_trials = goals.len() * strategies.len();
    println!(
        "\nRunning {} trials ({} goals x {} strategies)\n",
        total_trials,
        goals.len(),
        strategies.len()
    );

    // Setup progress bar
    let pb = ProgressBar::new(total_trials as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})")
            .unwrap()
            .progress_chars("#>-"),
    );

    // Create semaphore for concurrency control
    let semaphore = Arc::new(Semaphore::new(config.max_concurrency));
    let client = Arc::new(client);
    let pb = Arc::new(pb);

    // Build all trial tasks
    let mut handles = Vec::new();

    for goal in goals {
        for strategy_id in &strategies {
            let sem = Arc::clone(&semaphore);
            let client = Arc::clone(&client);
            let pb = Arc::clone(&pb);
            let goal_id = goal.id.clone();
            let mut request = PlanRequest::from(goal);
            request.strategy_id = Some(strategy_id.clone());

            let handle = tokio::spawn(async move {
                let _permit = sem.acquire().await.unwrap();
                let result = client.run_trial(&goal_id, &request).await;
                pb.inc(1);
                result
            });

            handles.push(handle);
        }
    }

    // Collect all results
    let mut results = Vec::new();
    for handle in handles {
        let result = handle.await.context("Trial task panicked")?;
        results.push(result);
    }

    pb.finish_with_message("All trials complete");

    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = ExperimentConfig::default();
        assert_eq!(config.max_concurrency, 3);
        assert_eq!(config.agent_url, "http://localhost:8000");
        assert!(config.strategies.is_none());
    }
}
