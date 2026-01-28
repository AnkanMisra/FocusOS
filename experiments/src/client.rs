//! HTTP client for the FocusOS Python agent API.

use anyhow::{Context, Result};
use reqwest::Client;
use std::time::{Duration, Instant};

use crate::models::{PlanRequest, PlanResponse, StrategiesResponse, TrialResult};

/// Client for interacting with the FocusOS agent API.
#[derive(Clone)]
pub struct AgentClient {
    client: Client,
    base_url: String,
}

impl AgentClient {
    /// Create a new agent client.
    pub fn new(base_url: &str) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(120)) // LLM calls can be slow
            .build()
            .context("Failed to create HTTP client")?;

        Ok(Self {
            client,
            base_url: base_url.trim_end_matches('/').to_string(),
        })
    }

    /// Check if the agent is healthy.
    pub async fn health_check(&self) -> Result<bool> {
        let resp = self
            .client
            .get(format!("{}/health", self.base_url))
            .send()
            .await
            .context("Health check request failed")?;

        Ok(resp.status().is_success())
    }

    /// Get available strategies.
    pub async fn get_strategies(&self) -> Result<StrategiesResponse> {
        let resp = self
            .client
            .get(format!("{}/strategies", self.base_url))
            .send()
            .await
            .context("Failed to fetch strategies")?;

        resp.json()
            .await
            .context("Failed to parse strategies response")
    }

    /// Generate a plan with evaluation.
    pub async fn generate_plan(
        &self,
        request: &PlanRequest,
        evaluate: bool,
    ) -> Result<PlanResponse> {
        let url = if evaluate {
            format!("{}/agent/plan?evaluate=true", self.base_url)
        } else {
            format!("{}/agent/plan", self.base_url)
        };

        let resp = self
            .client
            .post(&url)
            .json(request)
            .send()
            .await
            .context("Failed to send plan request")?;

        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            anyhow::bail!("Plan request failed with status {}: {}", status, body);
        }

        resp.json()
            .await
            .context("Failed to parse plan response")
    }

    /// Run a single trial (goal + strategy) and return the result.
    pub async fn run_trial(&self, goal_id: &str, goal_request: &PlanRequest) -> TrialResult {
        let start = Instant::now();
        let strategy_id = goal_request
            .strategy_id
            .clone()
            .unwrap_or_else(|| "default".to_string());

        match self.generate_plan(goal_request, true).await {
            Ok(plan) => TrialResult {
                goal_id: goal_id.to_string(),
                strategy_id,
                success: true,
                plan: Some(plan),
                error: None,
                duration_ms: start.elapsed().as_millis() as u64,
            },
            Err(e) => TrialResult {
                goal_id: goal_id.to_string(),
                strategy_id,
                success: false,
                plan: None,
                error: Some(e.to_string()),
                duration_ms: start.elapsed().as_millis() as u64,
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_creation() {
        let client = AgentClient::new("http://localhost:8000");
        assert!(client.is_ok());
    }

    #[test]
    fn test_base_url_normalization() {
        let client = AgentClient::new("http://localhost:8000/").unwrap();
        assert_eq!(client.base_url, "http://localhost:8000");
    }
}
