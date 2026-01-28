//! FocusOS Experiment Runner CLI
//!
//! A Rust CLI tool for running controlled experiments comparing agent strategies.
//!
//! Usage:
//!   run-experiment --name baseline_2026_01
//!   run-experiment --name test --strategies empathetic_25_light,strict_25_aggressive
//!   run-experiment --name custom --dataset goals.json

mod client;
mod datasets;
mod models;
mod results;
mod runner;

use anyhow::Result;
use clap::Parser;
use colored::Colorize;
use std::path::PathBuf;

use crate::datasets::default_dataset;
use crate::results::build_experiment_result;
use crate::runner::{run_trials, ExperimentConfig};

/// FocusOS Experiment Runner - Compare agent strategies systematically
#[derive(Parser, Debug)]
#[command(name = "run-experiment")]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Name for this experiment run
    #[arg(short, long, default_value = "experiment")]
    name: String,

    /// Agent API URL
    #[arg(short, long, default_value = "http://localhost:8000")]
    url: String,

    /// Strategies to test (comma-separated). If not specified, tests all available.
    #[arg(short, long, value_delimiter = ',')]
    strategies: Option<Vec<String>>,

    /// Custom dataset JSON file (uses built-in 12-goal dataset if not specified)
    #[arg(short, long)]
    dataset: Option<PathBuf>,

    /// Output directory for results
    #[arg(short, long, default_value = "results")]
    output: PathBuf,

    /// Maximum concurrent API requests
    #[arg(short, long, default_value = "3")]
    concurrency: usize,

    /// Print detailed trial results
    #[arg(long)]
    verbose: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Print banner
    println!("\n{}", "=".repeat(60).cyan());
    println!("{}", "  FocusOS Experiment Runner".cyan().bold());
    println!("{}\n", "=".repeat(60).cyan());

    // Load goals
    let goals = if let Some(path) = &args.dataset {
        println!("Loading dataset from: {}", path.display());
        datasets::load_from_file(path)?
    } else {
        println!("Using default dataset (12 goals)");
        default_dataset()
    };

    println!("Experiment: {}", args.name.yellow());
    println!("Agent URL: {}", args.url);
    println!("Goals: {}", goals.len());
    if let Some(ref strategies) = args.strategies {
        println!("Strategies: {}", strategies.join(", "));
    } else {
        println!("Strategies: all available");
    }
    println!("Concurrency: {}", args.concurrency);

    // Configure experiment
    let config = ExperimentConfig {
        max_concurrency: args.concurrency,
        agent_url: args.url,
        strategies: args.strategies,
    };

    // Run trials
    let trials = run_trials(&goals, &config).await?;

    // Build results
    let result = build_experiment_result(&args.name, goals.len(), trials);

    // Print summary
    println!("\n{}", "=".repeat(60).green());
    println!("{}", "  Results Summary".green().bold());
    println!("{}\n", "=".repeat(60).green());

    println!("{}: {}", "Best Overall".bold(), result.best_overall.green());
    println!();

    // Print strategy comparison table
    println!("{}", "Strategy Scores:".bold());
    println!(
        "{:<25} {:>8} {:>8} {:>8} {:>8} {:>8}",
        "Strategy", "Clarity", "Realism", "Align", "Motiv", "Overall"
    );
    println!("{}", "-".repeat(73));

    for stat in &result.strategy_stats {
        let is_best = stat.strategy_id == result.best_overall;
        let row = format!(
            "{:<25} {:>8.1} {:>8.1} {:>8.1} {:>8.1} {:>8.2}",
            stat.strategy_id,
            stat.task_clarity.mean,
            stat.workload_realism.mean,
            stat.goal_alignment.mean,
            stat.motivation_quality.mean,
            stat.overall.mean
        );
        if is_best {
            println!("{}", row.green().bold());
        } else {
            println!("{}", row);
        }
    }

    println!();
    println!("{}", "Dimension Winners:".bold());
    for winner in &result.dimension_winners {
        println!(
            "  {:<20} {} ({:.1})",
            winner.dimension,
            winner.winner.green(),
            winner.score
        );
    }

    // Print failures if any
    let failures: Vec<_> = result.trials.iter().filter(|t| !t.success).collect();
    if !failures.is_empty() {
        println!("\n{}", "Failures:".red().bold());
        for f in &failures {
            println!(
                "  {} + {}: {}",
                f.goal_id,
                f.strategy_id,
                f.error.as_deref().unwrap_or("unknown error")
            );
        }
    }

    // Verbose output
    if args.verbose {
        println!("\n{}", "Detailed Trial Results:".bold());
        for trial in &result.trials {
            if trial.success {
                if let Some(ref plan) = trial.plan {
                    if let Some(ref eval) = plan.evaluation {
                        println!(
                            "  {} + {} -> {:.1} (clarity={}, realism={}, align={}, motiv={})",
                            trial.goal_id,
                            trial.strategy_id,
                            eval.overall_score,
                            eval.task_clarity.score,
                            eval.workload_realism.score,
                            eval.goal_alignment.score,
                            eval.motivation_quality.score
                        );
                    }
                }
            }
        }
    }

    // Save results to JSON
    std::fs::create_dir_all(&args.output)?;
    let timestamp = chrono::Utc::now().format("%Y%m%d_%H%M%S");
    let output_path = args.output.join(format!("{}_{}.json", args.name, timestamp));
    let json = serde_json::to_string_pretty(&result)?;
    std::fs::write(&output_path, &json)?;

    println!("\n{}", "=".repeat(60).cyan());
    println!("Results saved to: {}", output_path.display().to_string().cyan());
    println!("{}\n", "=".repeat(60).cyan());

    Ok(())
}
