//! Predefined test datasets for FocusOS experiments.
//!
//! Contains 12 diverse goals covering different scenarios:
//! - Time availability: short (30-60min), medium (90-120min), long (180-240min)
//! - Energy levels: low, medium, high
//! - Goal types: technical, creative, administrative, learning

use crate::models::{EnergyLevel, ExperimentGoal};

/// Returns the default experiment dataset with 12 diverse goals.
pub fn default_dataset() -> Vec<ExperimentGoal> {
    vec![
        // === SHORT SESSIONS (30-60 min) ===
        ExperimentGoal {
            id: "short_high_tech".to_string(),
            goal_text: "Fix the authentication bug in the login flow".to_string(),
            available_minutes: 45,
            energy_level: EnergyLevel::High,
            category: "technical".to_string(),
        },
        ExperimentGoal {
            id: "short_low_admin".to_string(),
            goal_text: "Review and respond to pending emails".to_string(),
            available_minutes: 30,
            energy_level: EnergyLevel::Low,
            category: "administrative".to_string(),
        },
        ExperimentGoal {
            id: "short_medium_creative".to_string(),
            goal_text: "Brainstorm ideas for the new feature announcement".to_string(),
            available_minutes: 40,
            energy_level: EnergyLevel::Medium,
            category: "creative".to_string(),
        },
        ExperimentGoal {
            id: "short_high_learning".to_string(),
            goal_text: "Complete one chapter of the Rust programming book".to_string(),
            available_minutes: 60,
            energy_level: EnergyLevel::High,
            category: "learning".to_string(),
        },
        // === MEDIUM SESSIONS (90-120 min) ===
        ExperimentGoal {
            id: "medium_high_tech".to_string(),
            goal_text: "Implement the user dashboard API endpoints and write tests".to_string(),
            available_minutes: 120,
            energy_level: EnergyLevel::High,
            category: "technical".to_string(),
        },
        ExperimentGoal {
            id: "medium_medium_multitask".to_string(),
            goal_text: "Review 3 pull requests and update project documentation".to_string(),
            available_minutes: 90,
            energy_level: EnergyLevel::Medium,
            category: "technical".to_string(),
        },
        ExperimentGoal {
            id: "medium_low_creative".to_string(),
            goal_text: "Design wireframes for the settings page redesign".to_string(),
            available_minutes: 100,
            energy_level: EnergyLevel::Low,
            category: "creative".to_string(),
        },
        ExperimentGoal {
            id: "medium_high_learning".to_string(),
            goal_text: "Study system design patterns and take notes on caching strategies".to_string(),
            available_minutes: 90,
            energy_level: EnergyLevel::High,
            category: "learning".to_string(),
        },
        // === LONG SESSIONS (180-240 min) ===
        ExperimentGoal {
            id: "long_high_tech".to_string(),
            goal_text: "Build the complete checkout flow including payment integration".to_string(),
            available_minutes: 240,
            energy_level: EnergyLevel::High,
            category: "technical".to_string(),
        },
        ExperimentGoal {
            id: "long_medium_multitask".to_string(),
            goal_text: "Prepare quarterly report, update roadmap, and draft team newsletter".to_string(),
            available_minutes: 180,
            energy_level: EnergyLevel::Medium,
            category: "administrative".to_string(),
        },
        ExperimentGoal {
            id: "long_low_creative".to_string(),
            goal_text: "Write blog post about our engineering culture and review drafts".to_string(),
            available_minutes: 180,
            energy_level: EnergyLevel::Low,
            category: "creative".to_string(),
        },
        ExperimentGoal {
            id: "long_high_complex".to_string(),
            goal_text: "Refactor the database layer to use connection pooling and update all dependent services".to_string(),
            available_minutes: 200,
            energy_level: EnergyLevel::High,
            category: "technical".to_string(),
        },
    ]
}

/// Returns goals filtered by category.
pub fn goals_by_category(category: &str) -> Vec<ExperimentGoal> {
    default_dataset()
        .into_iter()
        .filter(|g| g.category == category)
        .collect()
}

/// Returns goals filtered by energy level.
pub fn goals_by_energy(energy: EnergyLevel) -> Vec<ExperimentGoal> {
    default_dataset()
        .into_iter()
        .filter(|g| g.energy_level == energy)
        .collect()
}

/// Load goals from a JSON file.
pub fn load_from_file(path: &std::path::Path) -> anyhow::Result<Vec<ExperimentGoal>> {
    let content = std::fs::read_to_string(path)?;
    let goals: Vec<ExperimentGoal> = serde_json::from_str(&content)?;
    Ok(goals)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_dataset_has_12_goals() {
        let goals = default_dataset();
        assert_eq!(goals.len(), 12);
    }

    #[test]
    fn test_all_goals_have_unique_ids() {
        let goals = default_dataset();
        let mut ids: Vec<_> = goals.iter().map(|g| &g.id).collect();
        ids.sort();
        ids.dedup();
        assert_eq!(ids.len(), 12);
    }

    #[test]
    fn test_goals_cover_all_energy_levels() {
        let goals = default_dataset();
        assert!(goals.iter().any(|g| g.energy_level == EnergyLevel::Low));
        assert!(goals.iter().any(|g| g.energy_level == EnergyLevel::Medium));
        assert!(goals.iter().any(|g| g.energy_level == EnergyLevel::High));
    }

    #[test]
    fn test_filter_by_category() {
        let tech_goals = goals_by_category("technical");
        assert!(!tech_goals.is_empty());
        assert!(tech_goals.iter().all(|g| g.category == "technical"));
    }
}
