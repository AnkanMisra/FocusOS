import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  daily_goals: defineTable({
    goal_text: v.string(),
    available_minutes: v.number(),
    energy_level: v.string(), // "low" | "medium" | "high"
    created_at: v.number(), // timestamp
    status: v.string(), // "pending", "planned", "completed"
  }),

  focus_plans: defineTable({
    goal_id: v.id("daily_goals"),
    strategy_id: v.string(),
    prompt_version: v.string(),
    total_minutes: v.number(),
    blocks: v.array(
      v.object({
        order: v.number(),
        duration_min: v.number(),
        task: v.string(),
        nudge: v.string(),
        completed: v.boolean(),
      })
    ),
    created_at: v.number(),
    evaluation: v.optional(
      v.object({
        task_clarity: v.object({ score: v.number(), reasoning: v.string() }),
        workload_realism: v.object({ score: v.number(), reasoning: v.string() }),
        goal_alignment: v.object({ score: v.number(), reasoning: v.string() }),
        motivation_quality: v.object({ score: v.number(), reasoning: v.string() }),
        overall_score: v.number(),
      })
    ),
  }).index("by_goal_id", ["goal_id"]),

  feedback: defineTable({
    plan_id: v.id("focus_plans"),
    completed: v.boolean(),
    perceived_difficulty: v.number(), // 1-5
    usefulness_score: v.number(), // 1-5
    free_text: v.optional(v.string()),
    created_at: v.number(),
  }),
});
